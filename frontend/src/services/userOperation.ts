/**
 * UserOperation 서비스
 * Account Abstraction 트랜잭션 생성 및 전송
 */
import { ethers } from 'ethers';
import apiClient from './api';
import { getProvider } from './web3';

export interface UserOperation {
  sender: string;
  nonce: number;
  initCode: string;
  callData: string;
  callGasLimit: number;
  verificationGasLimit: number;
  preVerificationGas: number;
  maxFeePerGas: number;
  maxPriorityFeePerGas: number;
  paymasterAndData: string;
  signature?: string;
}

/**
 * UserOperation 생성 (백엔드)
 */
export async function createUserOperation(
  target: string,
  data: string, // hex encoded bytes
  value: number = 0
): Promise<UserOperation> {
  try {
    const response = await apiClient.post('/user-operations/create', {
      target,
      data,
      value,
    });
    
    return response.data.user_operation;
  } catch (error: any) {
    console.error('[userOperation] Failed to create UserOperation:', error);
    throw new Error(error.response?.data?.detail || 'Failed to create UserOperation');
  }
}

/**
 * UserOperation 서명 (프론트엔드)
 * 
 * 주의: 실제로는 사용자의 private key가 필요하지만,
 * 현재는 백엔드에서 서명하도록 구현되어 있음
 * 향후 사용자 지갑에서 직접 서명하도록 변경 가능
 */
export async function signUserOperation(
  _userOperation: UserOperation,
  _privateKey?: string
): Promise<string> {
  // 현재는 백엔드에서 서명하므로 이 함수는 사용하지 않음
  // 향후 사용자 지갑에서 직접 서명할 때 사용
  throw new Error('Signing should be done on backend');
}

/**
 * UserOperation 전송 (백엔드)
 */
export async function sendUserOperation(
  userOperation: UserOperation,
  signature: string
): Promise<string> {
  try {
    const response = await apiClient.post('/user-operations/send', {
      user_operation: userOperation,
      signature,
    });
    
    return response.data.user_operation_hash;
  } catch (error: any) {
    console.error('[userOperation] Failed to send UserOperation:', error);
    throw new Error(error.response?.data?.detail || 'Failed to send UserOperation');
  }
}

/**
 * 컨트랙트 함수 호출을 위한 데이터 인코딩
 */
export function encodeFunctionCall(
  contractAddress: string,
  abi: any[],
  functionName: string,
  params: any[]
): string {
  const contract = new ethers.Contract(contractAddress, abi, getProvider());
  const iface = contract.interface;
  return iface.encodeFunctionData(functionName, params);
}

/**
 * 티켓 구매를 위한 UserOperation 생성 및 전송
 */
export async function purchaseTicketWithUserOperation(
  eventManagerAddress: string,
  eventId: string,
  priceWei: bigint
): Promise<string> {
  try {
    // EventManager ABI (purchaseTicket 함수)
    const eventManagerABI = [
      {
        inputs: [
          { name: 'eventId', type: 'uint256' },
        ],
        name: 'purchaseTicket',
        outputs: [],
        stateMutability: 'payable',
        type: 'function',
      },
    ];
    
    // 함수 호출 데이터 인코딩
    const callData = encodeFunctionCall(
      eventManagerAddress,
      eventManagerABI,
      'purchaseTicket',
      [eventId]
    );
    
    // UserOperation 생성
    const response = await createUserOperation(
      eventManagerAddress,
      callData,
      Number(priceWei)
    );
    
    // 백엔드에서 서명 및 전송 (signature 없이 전송하면 백엔드에서 자동 서명)
    const opHash = await sendUserOperation(response, '');
    
    return opHash;
  } catch (error: any) {
    console.error('[userOperation] Failed to purchase ticket with UserOperation:', error);
    throw error;
  }
}

