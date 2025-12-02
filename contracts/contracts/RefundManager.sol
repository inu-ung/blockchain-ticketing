// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./TicketAccessControl.sol";
import "./TicketNFT.sol";
import "./EventManager.sol";

/**
 * @title RefundManager
 * @dev 환불 관리 컨트랙트
 */
contract RefundManager is AccessControl, ReentrancyGuard {
    TicketAccessControl public accessControl;
    TicketNFT public ticketNFT;
    EventManager public eventManager;

    // 이더 수신을 위한 receive 함수
    receive() external payable {}

    struct RefundRequest {
        uint256 tokenId;
        address requester;
        uint256 refundAmount;
        bool processed;
        uint256 requestedAt;
        uint256 processedAt;
    }

    // 토큰 ID => 환불 요청
    mapping(uint256 => RefundRequest) public refundRequests;

    // 환불 가능 기간 (이벤트 시작 N일 전까지만, 기본 7일)
    uint256 public refundDeadlineDays = 7 days;

    // 환불 수수료 (기본 0%, 10000 = 100%)
    uint256 public refundFee = 0;
    uint256 public constant FEE_DENOMINATOR = 10000;

    event RefundRequested(
        uint256 indexed tokenId,
        address indexed requester,
        uint256 refundAmount
    );

    event RefundProcessed(
        uint256 indexed tokenId,
        address indexed requester,
        uint256 refundAmount,
        uint256 fee
    );

    event RefundDeadlineUpdated(uint256 newDeadline);
    event RefundFeeUpdated(uint256 newFee);

    modifier onlyAdmin() {
        require(
            accessControl.hasRole(accessControl.ADMIN_ROLE(), msg.sender),
            "RefundManager: must be admin"
        );
        _;
    }

    modifier onlyOrganizerOrAdmin(uint256 eventId) {
        EventManager.Event memory eventData = eventManager.getEvent(eventId);
        require(
            eventData.organizer == msg.sender ||
                accessControl.hasRole(accessControl.ADMIN_ROLE(), msg.sender),
            "RefundManager: not authorized"
        );
        _;
    }

    constructor(
        address _accessControl,
        address _ticketNFT,
        address _eventManager
    ) {
        accessControl = TicketAccessControl(_accessControl);
        ticketNFT = TicketNFT(_ticketNFT);
        eventManager = EventManager(_eventManager);
    }

    /**
     * @dev 환불 요청
     */
    function requestRefund(uint256 tokenId) external nonReentrant {
        require(
            ticketNFT.ownerOf(tokenId) == msg.sender,
            "RefundManager: not ticket owner"
        );
        require(
            !refundRequests[tokenId].processed,
            "RefundManager: refund already processed"
        );

        uint256 eventId = ticketNFT.tokenToEvent(tokenId);
        EventManager.Event memory eventData = eventManager.getEvent(eventId);

        // 환불 가능 기간 확인
        require(
            block.timestamp <= eventData.eventDate - refundDeadlineDays,
            "RefundManager: refund deadline passed"
        );

        // 이벤트 취소 확인
        require(!eventData.cancelled, "RefundManager: event is cancelled");

        // 환불 금액 계산
        uint256 refundAmount = eventData.price;
        if (refundFee > 0) {
            uint256 fee = (refundAmount * refundFee) / FEE_DENOMINATOR;
            refundAmount = refundAmount - fee;
        }

        refundRequests[tokenId] = RefundRequest({
            tokenId: tokenId,
            requester: msg.sender,
            refundAmount: refundAmount,
            processed: false,
            requestedAt: block.timestamp,
            processedAt: 0
        });

        emit RefundRequested(tokenId, msg.sender, refundAmount);
    }

    /**
     * @dev 환불 처리 (주최자 또는 관리자)
     */
    function processRefund(
        uint256 tokenId
    ) external onlyOrganizerOrAdmin(ticketNFT.tokenToEvent(tokenId)) nonReentrant {
        RefundRequest storage request = refundRequests[tokenId];
        require(request.requester != address(0), "RefundManager: refund not requested");
        require(!request.processed, "RefundManager: already processed");

        uint256 eventId = ticketNFT.tokenToEvent(tokenId);
        EventManager.Event memory eventData = eventManager.getEvent(eventId);

        // 환불 금액 계산
        uint256 refundAmount = eventData.price;
        uint256 fee = 0;
        if (refundFee > 0) {
            fee = (refundAmount * refundFee) / FEE_DENOMINATOR;
            refundAmount = refundAmount - fee;
        }

        request.processed = true;
        request.processedAt = block.timestamp;
        request.refundAmount = refundAmount;

        // 티켓 소각
        ticketNFT.burnTicket(tokenId);

        // 환불 지불
        if (refundAmount > 0) {
            (bool success, ) = request.requester.call{value: refundAmount}("");
            require(success, "RefundManager: refund payment failed");
        }

        emit RefundProcessed(tokenId, request.requester, refundAmount, fee);
    }

    /**
     * @dev 긴급 환불 (관리자만, 이벤트 취소 시)
     */
    function emergencyRefund(uint256 tokenId) external onlyAdmin nonReentrant {
        require(
            ticketNFT.ownerOf(tokenId) != address(0),
            "RefundManager: ticket does not exist"
        );

        uint256 eventId = ticketNFT.tokenToEvent(tokenId);
        EventManager.Event memory eventData = eventManager.getEvent(eventId);

        // 이벤트 취소 확인
        require(eventData.cancelled, "RefundManager: event not cancelled");

        uint256 refundAmount = eventData.price;

        // 티켓 소각
        ticketNFT.burnTicket(tokenId);

        address owner = ticketNFT.ownerOf(tokenId);
        if (owner != address(0)) {
            // 환불 지불
            (bool success, ) = owner.call{value: refundAmount}("");
            require(success, "RefundManager: refund payment failed");
        }

        emit RefundProcessed(tokenId, owner, refundAmount, 0);
    }

    /**
     * @dev 환불 가능 기간 업데이트 (관리자)
     */
    function setRefundDeadline(uint256 newDeadline) external onlyAdmin {
        refundDeadlineDays = newDeadline;
        emit RefundDeadlineUpdated(newDeadline);
    }

    /**
     * @dev 환불 수수료 업데이트 (관리자)
     */
    function setRefundFee(uint256 newFee) external onlyAdmin {
        require(newFee < FEE_DENOMINATOR, "RefundManager: fee too high");
        refundFee = newFee;
        emit RefundFeeUpdated(newFee);
    }

    /**
     * @dev 환불 요청 조회
     */
    function getRefundRequest(uint256 tokenId) external view returns (RefundRequest memory) {
        return refundRequests[tokenId];
    }

    /**
     * @dev 환불 가능 여부 확인
     */
    function isRefundable(uint256 tokenId) external view returns (bool) {
        uint256 eventId = ticketNFT.tokenToEvent(tokenId);
        EventManager.Event memory eventData = eventManager.getEvent(eventId);

        if (eventData.cancelled) return true;
        if (block.timestamp > eventData.eventDate - refundDeadlineDays) return false;

        return true;
    }
}

