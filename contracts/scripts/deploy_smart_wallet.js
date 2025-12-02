const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * Smart Wallet 배포 스크립트
 * 
 * 설명:
 * 1. EntryPoint 주소 확인 (ERC-4337 표준 주소 사용)
 * 2. SmartWallet 구현 컨트랙트 배포
 * 3. SmartWalletFactory 배포
 * 4. 배포 정보 저장
 */
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying Smart Wallet with account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  // ERC-4337 표준 EntryPoint 주소
  // 로컬 테스트: 실제 EntryPoint 배포 필요
  // 테스트넷/메인넷: 표준 주소 사용
  const ENTRY_POINT_ADDRESS = process.env.ENTRY_POINT_ADDRESS || 
    "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"; // 표준 EntryPoint 주소

  console.log("\n=== Smart Wallet 배포 시작 ===");
  console.log("EntryPoint 주소:", ENTRY_POINT_ADDRESS);

  // 1. SmartWallet 구현 컨트랙트 배포
  console.log("\n1. Deploying SmartWallet implementation...");
  const SmartWallet = await hre.ethers.getContractFactory("SmartWallet");
  const smartWallet = await SmartWallet.deploy(ENTRY_POINT_ADDRESS);
  await smartWallet.waitForDeployment();
  const smartWalletAddress = await smartWallet.getAddress();
  console.log("✅ SmartWallet deployed to:", smartWalletAddress);

  // 2. SmartWalletFactory 배포
  console.log("\n2. Deploying SmartWalletFactory...");
  const SmartWalletFactory = await hre.ethers.getContractFactory("SmartWalletFactory");
  const factory = await SmartWalletFactory.deploy(ENTRY_POINT_ADDRESS);
  await factory.waitForDeployment();
  const factoryAddress = await factory.getAddress();
  console.log("✅ SmartWalletFactory deployed to:", factoryAddress);

  // 3. 배포 정보 저장
  const networkName = hre.network.name;
  const deploymentDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentDir)) {
    fs.mkdirSync(deploymentDir, { recursive: true });
  }

  const deploymentFile = path.join(deploymentDir, `${networkName}.json`);
  let deploymentInfo = {};
  
  if (fs.existsSync(deploymentFile)) {
    deploymentInfo = JSON.parse(fs.readFileSync(deploymentFile, "utf8"));
  }

  deploymentInfo.contracts = deploymentInfo.contracts || {};
  deploymentInfo.contracts.SmartWallet = smartWalletAddress;
  deploymentInfo.contracts.SmartWalletFactory = factoryAddress;
  deploymentInfo.contracts.EntryPoint = ENTRY_POINT_ADDRESS;

  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

  console.log("\n=== 배포 완료 ===");
  console.log("Network:", networkName);
  console.log("Deployer:", deployer.address);
  console.log("\nContract Addresses:");
  console.log("  SmartWallet:", smartWalletAddress);
  console.log("  SmartWalletFactory:", factoryAddress);
  console.log("  EntryPoint:", ENTRY_POINT_ADDRESS);
  console.log("\nDeployment info saved to:", deploymentFile);

  // 4. 테스트: Smart Wallet 주소 계산
  console.log("\n=== 테스트: Smart Wallet 주소 계산 ===");
  const testOwner = deployer.address;
  const testSalt = 12345;
  const calculatedAddress = await factory.getAddress(testOwner, testSalt);
  console.log("Owner:", testOwner);
  console.log("Salt:", testSalt);
  console.log("Calculated Wallet Address:", calculatedAddress);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

