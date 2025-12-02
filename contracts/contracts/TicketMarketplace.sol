// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "./TicketAccessControl.sol";
import "./TicketNFT.sol";
import "./EventManager.sol";

/**
 * @title TicketMarketplace
 * @dev 2차 시장 재판매 마켓플레이스
 */
contract TicketMarketplace is AccessControl, ReentrancyGuard {
    TicketAccessControl public accessControl;
    TicketNFT public ticketNFT;
    EventManager public eventManager;

    struct Listing {
        uint256 tokenId;
        address seller;
        uint256 price;
        bool active;
        uint256 listedAt;
    }

    // 토큰 ID => 리스팅 정보
    mapping(uint256 => Listing) public listings;

    // 판매자 => 리스팅된 토큰 ID 목록
    mapping(address => uint256[]) public sellerListings;

    // 수수료 설정 (기본 5%, 10000 = 100%)
    uint256 public platformFee = 500; // 5%
    uint256 public constant MAX_FEE = 1000; // 10%
    uint256 public constant FEE_DENOMINATOR = 10000;

    // 가격 상한선 배수 (기본 200%, 20000 = 200%)
    uint256 public maxPriceMultiplier = 20000; // 200%
    uint256 public constant PRICE_DENOMINATOR = 10000;

    // 수수료 수령 주소
    address public feeRecipient;

    event TicketListed(
        uint256 indexed tokenId,
        address indexed seller,
        uint256 price
    );

    event TicketSold(
        uint256 indexed tokenId,
        address indexed seller,
        address indexed buyer,
        uint256 price,
        uint256 fee
    );

    event ListingCancelled(uint256 indexed tokenId);

    event PlatformFeeUpdated(uint256 newFee);
    event MaxPriceMultiplierUpdated(uint256 newMultiplier);

    modifier onlyAdmin() {
        require(
            accessControl.hasRole(accessControl.ADMIN_ROLE(), msg.sender),
            "TicketMarketplace: must be admin"
        );
        _;
    }

    constructor(
        address _accessControl,
        address _ticketNFT,
        address _eventManager,
        address _feeRecipient
    ) {
        accessControl = TicketAccessControl(_accessControl);
        ticketNFT = TicketNFT(_ticketNFT);
        eventManager = EventManager(_eventManager);
        feeRecipient = _feeRecipient;
    }

    /**
     * @dev 티켓 재판매 등록
     */
    function listTicketForResale(
        uint256 tokenId,
        uint256 price
    ) external nonReentrant {
        require(
            ticketNFT.ownerOf(tokenId) == msg.sender,
            "TicketMarketplace: not ticket owner"
        );
        require(price > 0, "TicketMarketplace: price must be greater than 0");
        require(!listings[tokenId].active, "TicketMarketplace: already listed");

        // 가격 상한선 검증
        uint256 eventId = ticketNFT.tokenToEvent(tokenId);
        EventManager.Event memory eventData = eventManager.getEvent(eventId);
        uint256 maxPrice = (eventData.price * maxPriceMultiplier) / PRICE_DENOMINATOR;
        require(price <= maxPrice, "TicketMarketplace: price exceeds maximum");

        // 소유자가 마켓플레이스에 전송 권한을 부여해야 함 (테스트에서 처리)

        listings[tokenId] = Listing({
            tokenId: tokenId,
            seller: msg.sender,
            price: price,
            active: true,
            listedAt: block.timestamp
        });

        sellerListings[msg.sender].push(tokenId);

        emit TicketListed(tokenId, msg.sender, price);
    }

    /**
     * @dev 재판매 티켓 구매
     */
    function buyResaleTicket(uint256 tokenId) external payable nonReentrant {
        Listing storage listing = listings[tokenId];
        require(listing.active, "TicketMarketplace: ticket not listed");
        require(msg.sender != listing.seller, "TicketMarketplace: cannot buy own ticket");
        require(msg.value >= listing.price, "TicketMarketplace: insufficient payment");

        listing.active = false;

        // 수수료 계산
        uint256 fee = (listing.price * platformFee) / FEE_DENOMINATOR;
        uint256 sellerAmount = listing.price - fee;

        // 티켓 전송
        ticketNFT.safeTransferFrom(listing.seller, msg.sender, tokenId);

        // 판매자에게 지불
        (bool success1, ) = listing.seller.call{value: sellerAmount}("");
        require(success1, "TicketMarketplace: payment to seller failed");

        // 수수료 수령
        if (fee > 0) {
            (bool success2, ) = feeRecipient.call{value: fee}("");
            require(success2, "TicketMarketplace: fee payment failed");
        }

        // 초과 지불액 반환
        if (msg.value > listing.price) {
            (bool success3, ) = msg.sender.call{value: msg.value - listing.price}("");
            require(success3, "TicketMarketplace: refund failed");
        }

        emit TicketSold(tokenId, listing.seller, msg.sender, listing.price, fee);
    }

    /**
     * @dev 재판매 등록 취소
     */
    function cancelListing(uint256 tokenId) external nonReentrant {
        Listing storage listing = listings[tokenId];
        require(listing.active, "TicketMarketplace: not listed");
        require(
            listing.seller == msg.sender,
            "TicketMarketplace: not listing owner"
        );

        listing.active = false;
        emit ListingCancelled(tokenId);
    }

    /**
     * @dev 플랫폼 수수료 업데이트 (관리자)
     */
    function setPlatformFee(uint256 newFee) external onlyAdmin {
        require(newFee <= MAX_FEE, "TicketMarketplace: fee too high");
        platformFee = newFee;
        emit PlatformFeeUpdated(newFee);
    }

    /**
     * @dev 가격 상한선 배수 업데이트 (관리자)
     */
    function setMaxPriceMultiplier(uint256 newMultiplier) external onlyAdmin {
        require(newMultiplier >= PRICE_DENOMINATOR, "TicketMarketplace: multiplier too low");
        maxPriceMultiplier = newMultiplier;
        emit MaxPriceMultiplierUpdated(newMultiplier);
    }

    /**
     * @dev 수수료 수령 주소 업데이트 (관리자)
     */
    function setFeeRecipient(address newRecipient) external onlyAdmin {
        require(newRecipient != address(0), "TicketMarketplace: invalid address");
        feeRecipient = newRecipient;
    }

    /**
     * @dev 리스팅 정보 조회
     */
    function getListing(uint256 tokenId) external view returns (Listing memory) {
        return listings[tokenId];
    }

    /**
     * @dev 판매자의 리스팅 목록 조회
     */
    function getSellerListings(address seller) external view returns (uint256[] memory) {
        return sellerListings[seller];
    }
}

