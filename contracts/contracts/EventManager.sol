// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./TicketAccessControl.sol";
import "./TicketNFT.sol";

/**
 * @title EventManager
 * @dev 이벤트 생성 및 관리 컨트랙트
 */
contract EventManager is AccessControl, ReentrancyGuard {
    TicketAccessControl public accessControl;
    TicketNFT public ticketNFT;

    struct Event {
        uint256 eventId;
        address organizer;
        string ipfsHash;
        uint256 price;
        uint256 maxTickets;
        uint256 soldTickets;
        uint256 startTime;
        uint256 endTime;
        uint256 eventDate;
        bool approved;
        bool cancelled;
    }

    // 이벤트 ID => 이벤트 정보
    mapping(uint256 => Event) public events;

    // 주최자 => 이벤트 ID 목록
    mapping(address => uint256[]) public organizerEvents;

    // 이벤트 ID 카운터
    uint256 private _eventIdCounter;

    // 이벤트 상태
    enum EventStatus {
        Pending,
        Approved,
        Active,
        Cancelled,
        Ended
    }

    event EventCreated(
        uint256 indexed eventId,
        address indexed organizer,
        string ipfsHash,
        uint256 price,
        uint256 maxTickets
    );

    event EventApproved(uint256 indexed eventId, address indexed admin);
    event EventUpdated(uint256 indexed eventId, uint256 newPrice);
    event EventCancelled(uint256 indexed eventId);
    event TicketSold(
        uint256 indexed eventId,
        uint256 indexed tokenId,
        address indexed buyer,
        uint256 price
    );

    modifier onlyOrganizerOrAdmin(uint256 eventId) {
        require(
            events[eventId].organizer == msg.sender ||
                accessControl.hasRole(accessControl.ADMIN_ROLE(), msg.sender),
            "EventManager: not authorized"
        );
        _;
    }

    constructor(address _accessControl, address _ticketNFT) {
        accessControl = TicketAccessControl(_accessControl);
        ticketNFT = TicketNFT(_ticketNFT);
    }

    /**
     * @dev 이벤트 생성
     */
    function createEvent(
        string memory ipfsHash,
        uint256 price,
        uint256 maxTickets,
        uint256 startTime,
        uint256 endTime,
        uint256 eventDate
    ) external returns (uint256) {
        require(
            accessControl.hasRole(accessControl.ORGANIZER_ROLE(), msg.sender),
            "EventManager: must be organizer"
        );
        require(price > 0, "EventManager: price must be greater than 0");
        require(maxTickets > 0, "EventManager: maxTickets must be greater than 0");
        require(startTime < endTime, "EventManager: invalid time range");
        require(
            endTime <= eventDate,
            "EventManager: sale end time must be before event date"
        );

        uint256 eventId = _eventIdCounter;
        _eventIdCounter++;

        events[eventId] = Event({
            eventId: eventId,
            organizer: msg.sender,
            ipfsHash: ipfsHash,
            price: price,
            maxTickets: maxTickets,
            soldTickets: 0,
            startTime: startTime,
            endTime: endTime,
            eventDate: eventDate,
            approved: false,
            cancelled: false
        });

        organizerEvents[msg.sender].push(eventId);

        emit EventCreated(eventId, msg.sender, ipfsHash, price, maxTickets);
        return eventId;
    }

    /**
     * @dev 이벤트 승인 (관리자)
     */
    function approveEvent(uint256 eventId) external {
        require(
            accessControl.hasRole(accessControl.ADMIN_ROLE(), msg.sender),
            "EventManager: must be admin"
        );
        require(events[eventId].eventId == eventId, "EventManager: event does not exist");
        require(!events[eventId].approved, "EventManager: event already approved");
        require(!events[eventId].cancelled, "EventManager: event is cancelled");

        events[eventId].approved = true;
        emit EventApproved(eventId, msg.sender);
    }

    /**
     * @dev 이벤트 가격 수정
     */
    function updateEventPrice(
        uint256 eventId,
        uint256 newPrice
    ) external onlyOrganizerOrAdmin(eventId) {
        require(events[eventId].eventId == eventId, "EventManager: event does not exist");
        require(newPrice > 0, "EventManager: price must be greater than 0");
        require(
            events[eventId].soldTickets == 0,
            "EventManager: cannot change price after tickets sold"
        );

        events[eventId].price = newPrice;
        emit EventUpdated(eventId, newPrice);
    }

    /**
     * @dev 이벤트 취소
     */
    function cancelEvent(uint256 eventId) external onlyOrganizerOrAdmin(eventId) {
        require(events[eventId].eventId == eventId, "EventManager: event does not exist");
        require(!events[eventId].cancelled, "EventManager: event already cancelled");

        events[eventId].cancelled = true;
        emit EventCancelled(eventId);
    }

    /**
     * @dev 티켓 구매 (EventManager가 TicketNFT의 MINTER_ROLE을 가져야 함)
     */
    function purchaseTicket(
        uint256 eventId,
        string memory tokenURI
    ) external payable nonReentrant returns (uint256) {
        Event storage eventData = events[eventId];

        require(eventData.eventId == eventId, "EventManager: event does not exist");
        require(eventData.approved, "EventManager: event not approved");
        require(!eventData.cancelled, "EventManager: event is cancelled");
        require(
            block.timestamp >= eventData.startTime && block.timestamp <= eventData.endTime,
            "EventManager: not in sale period"
        );
        require(
            eventData.soldTickets < eventData.maxTickets,
            "EventManager: tickets sold out"
        );
        require(msg.value >= eventData.price, "EventManager: insufficient payment");

        // 티켓 발행
        uint256 tokenId = ticketNFT.mintTicket(msg.sender, eventId, tokenURI);
        eventData.soldTickets++;

        // 주최자에게 지불
        if (msg.value > 0) {
            (bool success, ) = eventData.organizer.call{value: msg.value}("");
            require(success, "EventManager: payment failed");
        }

        emit TicketSold(eventId, tokenId, msg.sender, eventData.price);
        return tokenId;
    }

    /**
     * @dev 이벤트 정보 조회 (개별 필드)
     */
    function getEventOrganizer(uint256 eventId) external view returns (address) {
        return events[eventId].organizer;
    }

    function getEventPrice(uint256 eventId) external view returns (uint256) {
        return events[eventId].price;
    }

    function getEventMaxTickets(uint256 eventId) external view returns (uint256) {
        return events[eventId].maxTickets;
    }

    function getEventApproved(uint256 eventId) external view returns (bool) {
        return events[eventId].approved;
    }

    /**
     * @dev 이벤트 정보 조회
     */
    function getEvent(uint256 eventId) external view returns (Event memory) {
        return events[eventId];
    }

    /**
     * @dev 이벤트 상태 조회
     */
    function getEventStatus(uint256 eventId) external view returns (EventStatus) {
        Event memory eventData = events[eventId];
        if (eventData.cancelled) return EventStatus.Cancelled;
        if (!eventData.approved) return EventStatus.Pending;
        if (block.timestamp < eventData.startTime) return EventStatus.Approved;
        if (
            block.timestamp >= eventData.startTime &&
            block.timestamp <= eventData.endTime
        ) return EventStatus.Active;
        return EventStatus.Ended;
    }

    /**
     * @dev 주최자의 이벤트 목록 조회
     */
    function getOrganizerEvents(address organizer) external view returns (uint256[] memory) {
        return organizerEvents[organizer];
    }

    /**
     * @dev 현재 이벤트 ID 카운터 반환
     */
    function getCurrentEventId() external view returns (uint256) {
        return _eventIdCounter;
    }
}
