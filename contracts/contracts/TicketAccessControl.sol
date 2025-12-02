// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title AccessControl
 * @dev 관리자와 주최자 권한을 관리하는 컨트랙트
 */
contract TicketAccessControl is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant ORGANIZER_ROLE = keccak256("ORGANIZER_ROLE");

    event AdminAdded(address indexed account);
    event AdminRemoved(address indexed account);
    event OrganizerAdded(address indexed account);
    event OrganizerRemoved(address indexed account);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
    }

    /**
     * @dev 관리자 추가
     */
    function addAdmin(address account) external onlyRole(ADMIN_ROLE) {
        _grantRole(ADMIN_ROLE, account);
        emit AdminAdded(account);
    }

    /**
     * @dev 관리자 제거
     */
    function removeAdmin(address account) external onlyRole(ADMIN_ROLE) {
        _revokeRole(ADMIN_ROLE, account);
        emit AdminRemoved(account);
    }

    /**
     * @dev 주최자 추가
     */
    function addOrganizer(address account) external onlyRole(ADMIN_ROLE) {
        _grantRole(ORGANIZER_ROLE, account);
        emit OrganizerAdded(account);
    }

    /**
     * @dev 주최자 제거
     */
    function removeOrganizer(address account) external onlyRole(ADMIN_ROLE) {
        _revokeRole(ORGANIZER_ROLE, account);
        emit OrganizerRemoved(account);
    }

    /**
     * @dev 관리자인지 확인
     */
    function isAdmin(address account) external view returns (bool) {
        return hasRole(ADMIN_ROLE, account);
    }

    /**
     * @dev 주최자인지 확인
     */
    function isOrganizer(address account) external view returns (bool) {
        return hasRole(ORGANIZER_ROLE, account);
    }
}

