const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * 전체 컨트랙트 배포 스크립트 (테스트넷/메인넷용)
 * 
 * 배포 순서:
 * 1. TicketAccessControl
 * 2. TicketNFT
 * 3. EventManager
 * 4. TicketMarketplace
 * 5. RefundManager
 * 6. SmartWallet (구현)
 * 7. SmartWalletFactory
 * 8. 권한 설정
 */
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "ETH/MATIC");
  
  if (balance === 0n) {
    console.error("❌ Error: Account balance is 0. Please fund your account first.");
    process.exit(1);
  }

  // ERC-4337 표준 EntryPoint 주소
  const ENTRY_POINT_ADDRESS = process.env.ENTRY_POINT_ADDRESS || 
    "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789";

  console.log("\n=== 전체 컨트랙트 배포 시작 ===");
  console.log("Network:", hre.network.name);
  console.log("EntryPoint:", ENTRY_POINT_ADDRESS);

  const contracts = {};

  try {
    // 1. AccessControl 배포
    console.log("\n[1/7] Deploying TicketAccessControl...");
    const TicketAccessControl = await hre.ethers.getContractFactory("TicketAccessControl");
    const accessControl = await TicketAccessControl.deploy(deployer.address);
    await accessControl.waitForDeployment();
    contracts.TicketAccessControl = await accessControl.getAddress();
    console.log("✅ TicketAccessControl:", contracts.TicketAccessControl);

    // 2. TicketNFT 배포
    console.log("\n[2/7] Deploying TicketNFT...");
    const TicketNFT = await hre.ethers.getContractFactory("TicketNFT");
    const ticketNFT = await TicketNFT.deploy(deployer.address); // deployer를 admin으로 설정
    await ticketNFT.waitForDeployment();
    contracts.TicketNFT = await ticketNFT.getAddress();
    console.log("✅ TicketNFT:", contracts.TicketNFT);

    // 3. EventManager 배포
    console.log("\n[3/7] Deploying EventManager...");
    const EventManager = await hre.ethers.getContractFactory("EventManager");
    const eventManager = await EventManager.deploy(
      contracts.TicketAccessControl,
      contracts.TicketNFT
    );
    await eventManager.waitForDeployment();
    contracts.EventManager = await eventManager.getAddress();
    console.log("✅ EventManager:", contracts.EventManager);

    // 4. TicketMarketplace 배포
    console.log("\n[4/7] Deploying TicketMarketplace...");
    const TicketMarketplace = await hre.ethers.getContractFactory("TicketMarketplace");
    const marketplace = await TicketMarketplace.deploy(
      contracts.TicketAccessControl,
      contracts.TicketNFT,
      contracts.EventManager,
      deployer.address // feeRecipient
    );
    await marketplace.waitForDeployment();
    contracts.TicketMarketplace = await marketplace.getAddress();
    console.log("✅ TicketMarketplace:", contracts.TicketMarketplace);

    // 5. RefundManager 배포
    console.log("\n[5/7] Deploying RefundManager...");
    const RefundManager = await hre.ethers.getContractFactory("RefundManager");
    const refundManager = await RefundManager.deploy(
      contracts.TicketAccessControl,
      contracts.TicketNFT,
      contracts.EventManager
    );
    await refundManager.waitForDeployment();
    contracts.RefundManager = await refundManager.getAddress();
    console.log("✅ RefundManager:", contracts.RefundManager);

    // 6. SmartWallet 구현 배포
    console.log("\n[6/7] Deploying SmartWallet implementation...");
    const SmartWallet = await hre.ethers.getContractFactory("SmartWallet");
    const smartWallet = await SmartWallet.deploy(ENTRY_POINT_ADDRESS);
    await smartWallet.waitForDeployment();
    contracts.SmartWallet = await smartWallet.getAddress();
    console.log("✅ SmartWallet:", contracts.SmartWallet);

    // 7. SmartWalletFactory 배포
    console.log("\n[7/7] Deploying SmartWalletFactory...");
    const SmartWalletFactory = await hre.ethers.getContractFactory("SmartWalletFactory");
    const factory = await SmartWalletFactory.deploy(ENTRY_POINT_ADDRESS);
    await factory.waitForDeployment();
    contracts.SmartWalletFactory = await factory.getAddress();
    console.log("✅ SmartWalletFactory:", contracts.SmartWalletFactory);

    // 8. 권한 설정
    console.log("\n[8/8] Setting up roles...");
    
    // EventManager에 MINTER_ROLE 부여
    const MINTER_ROLE = await ticketNFT.MINTER_ROLE();
    const tx1 = await ticketNFT.grantRole(MINTER_ROLE, contracts.EventManager);
    await tx1.wait();
    console.log("✅ Granted MINTER_ROLE to EventManager");

    // RefundManager에 BURNER_ROLE 부여
    const BURNER_ROLE = await ticketNFT.BURNER_ROLE();
    const tx2 = await ticketNFT.grantRole(BURNER_ROLE, contracts.RefundManager);
    await tx2.wait();
    console.log("✅ Granted BURNER_ROLE to RefundManager");

    // 배포 정보 저장
    const networkName = hre.network.name;
    const deploymentDir = path.join(__dirname, "..", "deployments");
    if (!fs.existsSync(deploymentDir)) {
      fs.mkdirSync(deploymentDir, { recursive: true });
    }

    const deploymentInfo = {
      network: networkName,
      deployer: deployer.address,
      entryPoint: ENTRY_POINT_ADDRESS,
      contracts: contracts,
      timestamp: new Date().toISOString(),
    };

    const deploymentFile = path.join(deploymentDir, `${networkName}.json`);
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

    // 배포 요약 출력
    console.log("\n" + "=".repeat(60));
    console.log("🎉 배포 완료!");
    console.log("=".repeat(60));
    console.log("Network:", networkName);
    console.log("Deployer:", deployer.address);
    console.log("\n📋 Contract Addresses:");
    console.log("  TicketAccessControl:", contracts.TicketAccessControl);
    console.log("  TicketNFT:", contracts.TicketNFT);
    console.log("  EventManager:", contracts.EventManager);
    console.log("  TicketMarketplace:", contracts.TicketMarketplace);
    console.log("  RefundManager:", contracts.RefundManager);
    console.log("  SmartWallet:", contracts.SmartWallet);
    console.log("  SmartWalletFactory:", contracts.SmartWalletFactory);
    console.log("  EntryPoint:", ENTRY_POINT_ADDRESS);
    console.log("\n💾 Deployment info saved to:", deploymentFile);
    console.log("\n📝 다음 단계:");
    console.log("  1. 배포된 주소를 backend/.env에 추가");
    console.log("  2. 배포된 주소를 frontend/.env에 추가");
    console.log("  3. Polygonscan에서 컨트랙트 검증 (선택사항)");
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


