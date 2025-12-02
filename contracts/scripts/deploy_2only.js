const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * 최소 2개 컨트랙트만 배포 (가스비 최대 절약)
 * 
 * 필수 컨트랙트 (2개):
 * 1. TicketNFT - NFT 발행
 * 2. SmartWalletFactory - Smart Wallet 생성 (SmartWallet 포함)
 * 
 * EventManager 제거 - 백엔드에서 TicketNFT 직접 호출
 */
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying 2 contracts only with the account:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "ETH/MATIC");
  
  if (balance === 0n && hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.error("❌ Error: Account balance is 0. Please fund your account first.");
    process.exit(1);
  }

  // ERC-4337 표준 EntryPoint 주소
  const ENTRY_POINT_ADDRESS = process.env.ENTRY_POINT_ADDRESS || 
    "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789";

  console.log("\n" + "=".repeat(60));
  console.log("🚀 최소 2개 컨트랙트만 배포 (가스비 최대 절약)");
  console.log("=".repeat(60));
  console.log("Network:", hre.network.name);
  console.log("EntryPoint:", ENTRY_POINT_ADDRESS);
  console.log("\n💡 백엔드에서 처리:");
  console.log("   - EventManager (티켓 구매 로직)");
  console.log("   - AccessControl (역할 관리)");
  console.log("   - Marketplace (재판매)");
  console.log("   - RefundManager (환불)");
  console.log("=".repeat(60));

  const contracts = {};

  try {
    // 1. TicketNFT 배포
    console.log("\n[1/2] Deploying TicketNFT...");
    const TicketNFT = await hre.ethers.getContractFactory("TicketNFT");
    const ticketNFT = await TicketNFT.deploy(deployer.address);
    await ticketNFT.waitForDeployment();
    contracts.TicketNFT = await ticketNFT.getAddress();
    console.log("✅ TicketNFT:", contracts.TicketNFT);

    // 2. SmartWalletFactory 배포 (SmartWallet 구현 포함)
    console.log("\n[2/2] Deploying SmartWalletFactory...");
    const SmartWalletFactory = await hre.ethers.getContractFactory("SmartWalletFactory");
    const factory = await SmartWalletFactory.deploy(ENTRY_POINT_ADDRESS);
    await factory.waitForDeployment();
    contracts.SmartWalletFactory = await factory.getAddress();
    contracts.SmartWallet = await factory.walletImplementation();
    console.log("✅ SmartWalletFactory:", contracts.SmartWalletFactory);
    console.log("✅ SmartWallet (implementation):", contracts.SmartWallet);

    // 3. 백엔드 서비스 계정에 MINTER_ROLE 부여 (백엔드에서 직접 mintTicket 호출)
    console.log("\n[3/3] Setting up roles...");
    const MINTER_ROLE = await ticketNFT.MINTER_ROLE();
    // 백엔드 서비스 계정 주소 (환경 변수에서 가져오거나 deployer 사용)
    const backendServiceAddress = process.env.BACKEND_SERVICE_ADDRESS || deployer.address;
    const tx1 = await ticketNFT.grantRole(MINTER_ROLE, backendServiceAddress);
    await tx1.wait();
    console.log(`✅ Granted MINTER_ROLE to backend service: ${backendServiceAddress}`);

    // 배포 정보 저장
    const networkName = hre.network.name;
    const deploymentDir = path.join(__dirname, "..", "deployments");
    if (!fs.existsSync(deploymentDir)) {
      fs.mkdirSync(deploymentDir, { recursive: true });
    }

    const deploymentInfo = {
      network: networkName,
      deployer: deployer.address,
      backendServiceAddress: backendServiceAddress,
      entryPoint: ENTRY_POINT_ADDRESS,
      contracts: contracts,
      timestamp: new Date().toISOString(),
      note: "Only 2 contracts deployed - EventManager, AccessControl, Marketplace, RefundManager handled by backend"
    };

    const deploymentFile = path.join(deploymentDir, `${networkName}.json`);
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

    // 배포 요약 출력
    console.log("\n" + "=".repeat(60));
    console.log("🎉 2개 컨트랙트 배포 완료!");
    console.log("=".repeat(60));
    console.log("Network:", networkName);
    console.log("Deployer:", deployer.address);
    console.log("Backend Service:", backendServiceAddress);
    console.log("\n📋 배포된 Contract Addresses:");
    console.log("  1. TicketNFT:", contracts.TicketNFT);
    console.log("  2. SmartWalletFactory:", contracts.SmartWalletFactory);
    console.log("     └─ SmartWallet (impl):", contracts.SmartWallet);
    console.log("  EntryPoint:", ENTRY_POINT_ADDRESS);
    console.log("\n💡 백엔드에서 처리:");
    console.log("  - EventManager (티켓 구매 로직)");
    console.log("  - AccessControl (역할 관리)");
    console.log("  - Marketplace (재판매)");
    console.log("  - RefundManager (환불)");
    console.log("\n💾 Deployment info saved to:", deploymentFile);
    console.log("=".repeat(60));

  } catch (error) {
    console.error("\n❌ 배포 실패:", error);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

