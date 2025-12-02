// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "./SmartWallet.sol";
import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

/**
 * @title SmartWalletFactory
 * @dev Smart Wallet을 생성하는 Factory 컨트랙트
 * 
 * 설명:
 * - CREATE2를 사용하여 Deterministic 주소 생성
 * - 같은 owner와 salt로 항상 같은 주소 보장
 * - Proxy 패턴으로 가스비 절약
 */
contract SmartWalletFactory {
    // Smart Wallet 구현 컨트랙트 주소
    address public immutable walletImplementation;
    
    // EntryPoint 주소
    address public immutable entryPoint;
    
    // 배포된 지갑 주소 기록
    mapping(address => address) public wallets; // owner => wallet
    
    event WalletCreated(address indexed owner, address indexed wallet);
    
    /**
     * @dev 생성자
     * @param _entryPoint ERC-4337 EntryPoint 주소
     */
    constructor(address _entryPoint) {
        entryPoint = _entryPoint;
        
        // Smart Wallet 구현 컨트랙트 배포
        SmartWallet implementation = new SmartWallet(_entryPoint);
        walletImplementation = address(implementation);
    }
    
    /**
     * @dev Smart Wallet 주소 계산 (CREATE2)
     * @param owner Owner 주소
     * @param salt Salt 값
     * @return walletAddress 계산된 Smart Wallet 주소
     * 
     * 설명:
     * - CREATE2를 사용하여 Deterministic 주소 생성
     * - 같은 owner와 salt로 항상 같은 주소 반환
     * - 배포 전에도 주소를 미리 알 수 있음
     */
    function getAddress(address owner, uint256 salt) public view returns (address walletAddress) {
        bytes memory bytecode = abi.encodePacked(
            type(ERC1967Proxy).creationCode,
            abi.encode(
                walletImplementation,
                abi.encodeCall(SmartWallet.initialize, (owner))
            )
        );
        
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0xff),
                address(this),
                salt,
                keccak256(bytecode)
            )
        );
        
        walletAddress = address(uint160(uint256(hash)));
    }
    
    /**
     * @dev Smart Wallet 생성
     * @param owner Owner 주소
     * @param salt Salt 값 (사용자 ID 기반)
     * @return walletAddress 생성된 Smart Wallet 주소
     * 
     * 설명:
     * - Proxy 패턴으로 가스비 절약
     * - 이미 배포된 경우 기존 주소 반환
     */
    function createWallet(address owner, uint256 salt) external returns (address walletAddress) {
        // 이미 배포된 경우 기존 주소 반환
        if (wallets[owner] != address(0)) {
            return wallets[owner];
        }
        
        // 주소 계산
        walletAddress = getAddress(owner, salt);
        
        // 이미 배포되어 있는지 확인
        uint256 codeSize;
        assembly {
            codeSize := extcodesize(walletAddress)
        }
        if (codeSize > 0) {
            wallets[owner] = walletAddress;
            return walletAddress;
        }
        
        // Proxy 배포
        bytes memory bytecode = abi.encodePacked(
            type(ERC1967Proxy).creationCode,
            abi.encode(
                walletImplementation,
                abi.encodeCall(SmartWallet.initialize, (owner))
            )
        );
        
        assembly {
            walletAddress := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        }
        
        require(walletAddress != address(0), "SmartWalletFactory: creation failed");
        
        wallets[owner] = walletAddress;
        emit WalletCreated(owner, walletAddress);
    }
    
    /**
     * @dev 배포된 지갑 주소 조회
     * @param owner Owner 주소
     * @return walletAddress Smart Wallet 주소 (없으면 address(0))
     */
    function getWallet(address owner) external view returns (address walletAddress) {
        return wallets[owner];
    }
}

