const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * 자동 배포 스크립트 (CI/CD용)
 * 
 * 환경 변수:
 * - PRIVATE_KEY: 배포자 개인키
 * - NETWORK: 배포할 네트워크 (amoy, polygon)
 * - ENTRY_POINT_ADDRESS: ERC-4337 EntryPoint 주소
 * - SKIP_VERIFY: 검증 건너뛰기 (true/false)
 */
async function main() {
  const network = process.env.NETWORK || hre.network.name;
  const [deployer] = await hre.ethers.getSigners();
  
  console.log("=".repeat(60));
  console.log("🚀 자동 배포 시작");
  console.log("=".repeat(60));
  console.log("Network:", network);
  console.log("Deployer:", deployer.address);
  
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Balance:", hre.ethers.formatEther(balance), "ETH/MATIC");
  
  if (balance === 0n) {
    throw new Error("❌ Account balance is 0. Please fund your account first.");
  }

  // ERC-4337 표준 EntryPoint 주소
  const ENTRY_POINT_ADDRESS = process.env.ENTRY_POINT_ADDRESS || 
    "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789";

  console.log("EntryPoint:", ENTRY_POINT_ADDRESS);
  console.log("");

  const contracts = {};
  const deploymentDir = path.join(__dirname, "..", "deployments");
  
  if (!fs.existsSync(deploymentDir)) {
    fs.mkdirSync(deploymentDir, { recursive: true });
  }

  try {
    // 1. AccessControl 배포
    console.log("[1/7] Deploying TicketAccessControl...");
    const TicketAccessControl = await hre.ethers.getContractFactory("TicketAccessControl");
    const accessControl = await TicketAccessControl.deploy(deployer.address);
    await accessControl.waitForDeployment();
    contracts.TicketAccessControl = await accessControl.getAddress();
    console.log("✅ TicketAccessControl:", contracts.TicketAccessControl);

    // 2. TicketNFT 배포
    console.log("\n[2/7] Deploying TicketNFT...");
    const TicketNFT = await hre.ethers.getContractFactory("TicketNFT");
    const ticketNFT = await TicketNFT.deploy(contracts.TicketAccessControl);
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
    const deploymentInfo = {
      network: network,
      deployer: deployer.address,
      entryPoint: ENTRY_POINT_ADDRESS,
      contracts: contracts,
      timestamp: new Date().toISOString(),
      commitHash: process.env.GITHUB_SHA || "local",
      branch: process.env.GITHUB_REF_NAME || "local",
    };

    const deploymentFile = path.join(deploymentDir, `${network}.json`);
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

    // 배포 요약 출력
    console.log("\n" + "=".repeat(60));
    console.log("🎉 배포 완료!");
    console.log("=".repeat(60));
    console.log("Network:", network);
    console.log("Deployer:", deployer.address);
    console.log("\n📋 Contract Addresses:");
    Object.entries(contracts).forEach(([name, address]) => {
      console.log(`  ${name}:`, address);
    });
    console.log("  EntryPoint:", ENTRY_POINT_ADDRESS);
    console.log("\n💾 Deployment info saved to:", deploymentFile);
    console.log("=".repeat(60));

    // CI/CD 환경에서 JSON 출력 (다음 단계에서 사용)
    if (process.env.CI) {
      console.log("\n::set-output name=deployment_file::" + deploymentFile);
      console.log("\n::set-output name=network::" + network);
    }

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

