// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

/**
 * @title SmartWallet
 * @dev ERC-4337 기반 Smart Wallet 컨트랙트
 * 
 * 설명:
 * - 사용자 대신 트랜잭션을 실행하는 스마트 컨트랙트
 * - 서명 검증을 통해 사용자 권한 확인
 * - Paymaster를 통한 가스비 지불 지원
 */
contract SmartWallet is Initializable, UUPSUpgradeable {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // Owner 주소 (서비스 계정 또는 사용자)
    address public owner;
    
    // Nonce (재사용 공격 방지)
    uint256 public nonce;
    
    // EntryPoint 주소 (ERC-4337 표준)
    address public immutable entryPoint;
    
    event WalletInitialized(address indexed owner);
    event Executed(address indexed target, uint256 value, bytes data);
    
    /**
     * @dev 생성자
     * @param _entryPoint ERC-4337 EntryPoint 주소
     */
    constructor(address _entryPoint) {
        entryPoint = _entryPoint;
        // 생성자를 비활성화하여 Proxy 패턴 사용
        _disableInitializers();
    }
    
    /**
     * @dev 초기화 함수 (Proxy 배포 시 호출)
     * @param _owner Owner 주소
     */
    function initialize(address _owner) public initializer {
        owner = _owner;
        emit WalletInitialized(_owner);
    }
    
    /**
     * @dev execute 함수 (EntryPoint에서 호출)
     * @param target 호출할 컨트랙트 주소
     * @param value 전송할 이더 값
     * @param data 호출 데이터
     */
    function execute(
        address target,
        uint256 value,
        bytes calldata data
    ) external {
        // EntryPoint에서만 호출 가능
        require(msg.sender == entryPoint, "SmartWallet: only EntryPoint");
        
        // 컨트랙트 호출
        (bool success, ) = target.call{value: value}(data);
        require(success, "SmartWallet: execution failed");
        
        emit Executed(target, value, data);
    }
    
    /**
     * @dev validateUserOp (EntryPoint에서 호출)
     * @param userOp UserOperation 데이터
     * @param userOpHash UserOperation 해시
     * @param missingFunds 부족한 가스비
     * @return validationData 검증 결과
     */
    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingFunds
    ) external returns (uint256 validationData) {
        // EntryPoint에서만 호출 가능
        require(msg.sender == entryPoint, "SmartWallet: only EntryPoint");
        
        // 서명 검증
        bytes32 hash = userOpHash.toEthSignedMessageHash();
        address signer = ECDSA.recover(hash, userOp.signature);
        require(signer == owner, "SmartWallet: invalid signature");
        
        // Nonce 검증
        require(userOp.nonce == nonce, "SmartWallet: invalid nonce");
        nonce++;
        
        // 가스비 지불 (Paymaster가 처리)
        if (missingFunds > 0) {
            // Paymaster가 가스비를 지불하도록 허용
            // 실제로는 Paymaster 컨트랙트가 처리
        }
        
        return 0; // 검증 성공
    }
    
    /**
     * @dev UUPS 업그레이드 권한 확인
     */
    function _authorizeUpgrade(address /* newImplementation */) internal override {
        require(msg.sender == owner, "SmartWallet: only owner");
    }
    
    /**
     * @dev 이더 수신 허용
     */
    receive() external payable {}
    
    // UserOperation 구조체 (ERC-4337 표준)
    struct UserOperation {
        address sender;
        uint256 nonce;
        bytes initCode;
        bytes callData;
        uint256 callGasLimit;
        uint256 verificationGasLimit;
        uint256 preVerificationGas;
        uint256 maxFeePerGas;
        uint256 maxPriorityFeePerGas;
        bytes paymasterAndData;
        bytes signature;
    }
}

