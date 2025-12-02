// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title TicketNFT
 * @dev ERC-721 기반 티켓 NFT 컨트랙트
 */
contract TicketNFT is ERC721URIStorage, AccessControl, ReentrancyGuard {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");

    // 토큰 ID 카운터
    uint256 private _tokenIdCounter;

    // 토큰 ID => 이벤트 ID 매핑
    mapping(uint256 => uint256) public tokenToEvent;

    // 이벤트 ID => 발행된 티켓 수
    mapping(uint256 => uint256) public eventTicketCount;

    event TicketMinted(
        uint256 indexed tokenId,
        uint256 indexed eventId,
        address indexed to,
        string tokenURI
    );

    event TicketBurned(uint256 indexed tokenId);

    constructor(address admin) ERC721("TicketNFT", "TKT") {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, admin);
        _grantRole(BURNER_ROLE, admin);
    }

    /**
     * @dev 티켓 발행
     * @param to 티켓을 받을 주소
     * @param eventId 이벤트 ID
     * @param tokenURI IPFS 메타데이터 URI
     */
    function mintTicket(
        address to,
        uint256 eventId,
        string memory tokenURI
    ) external onlyRole(MINTER_ROLE) nonReentrant returns (uint256) {
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);
        tokenToEvent[tokenId] = eventId;
        eventTicketCount[eventId]++;

        emit TicketMinted(tokenId, eventId, to, tokenURI);
        return tokenId;
    }

    /**
     * @dev 티켓 소각 (환불 시 사용)
     */
    function burnTicket(uint256 tokenId) external onlyRole(BURNER_ROLE) {
        require(_ownerOf(tokenId) != address(0), "TicketNFT: token does not exist");
        uint256 eventId = tokenToEvent[tokenId];
        _burn(tokenId);
        eventTicketCount[eventId]--;
        emit TicketBurned(tokenId);
    }

    /**
     * @dev 토큰 전송 전 검증
     */
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal override returns (address) {
        return super._update(to, tokenId, auth);
    }

    /**
     * @dev 인터페이스 지원 확인
     */
    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC721URIStorage, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    /**
     * @dev 현재 토큰 ID 카운터 반환
     */
    function getCurrentTokenId() external view returns (uint256) {
        return _tokenIdCounter;
    }

    /**
     * @dev 이벤트의 발행된 티켓 수 조회
     */
    function getEventTicketCount(uint256 eventId) external view returns (uint256) {
        return eventTicketCount[eventId];
    }
}

