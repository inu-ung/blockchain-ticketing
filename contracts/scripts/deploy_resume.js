const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * 배포 재개 스크립트 (이미 배포된 컨트랙트 재사용)
 * 
 * 사용법:
 * 1. deployments/amoy.json 파일 확인
 * 2. 이미 배포된 컨트랙트 주소가 있으면 재사용
 * 3. 없는 컨트랙트만 배포
 */
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Resuming deployment with account:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "ETH/MATIC");
  
  if (balance === 0n) {
    console.error("❌ Error: Account balance is 0. Please fund your account first.");
    process.exit(1);
  }

  // ERC-4337 표준 EntryPoint 주소
  const ENTRY_POINT_ADDRESS = process.env.ENTRY_POINT_ADDRESS || 
    "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789";

  console.log("\n=== 배포 재개 ===");
  console.log("Network:", hre.network.name);
  console.log("EntryPoint:", ENTRY_POINT_ADDRESS);

  // 기존 배포 정보 로드
  const networkName = hre.network.name;
  const deploymentDir = path.join(__dirname, "..", "deployments");
  const deploymentFile = path.join(deploymentDir, `${networkName}.json`);
  
  let existingContracts = {};
  if (fs.existsSync(deploymentFile)) {
    const existing = JSON.parse(fs.readFileSync(deploymentFile, "utf8"));
    existingContracts = existing.contracts || {};
    console.log("\n기존 배포 정보 발견:");
    Object.keys(existingContracts).forEach(key => {
      console.log(`  ✅ ${key}: ${existingContracts[key]}`);
    });
  }

  const contracts = { ...existingContracts };

  try {
    // 1. AccessControl 배포 (없는 경우만)
    if (!contracts.TicketAccessControl) {
      console.log("\n[1/7] Deploying TicketAccessControl...");
      const TicketAccessControl = await hre.ethers.getContractFactory("TicketAccessControl");
      const accessControl = await TicketAccessControl.deploy(deployer.address);
      await accessControl.waitForDeployment();
      contracts.TicketAccessControl = await accessControl.getAddress();
      console.log("✅ TicketAccessControl:", contracts.TicketAccessControl);
    } else {
      console.log("\n[1/7] TicketAccessControl already deployed:", contracts.TicketAccessControl);
    }

    // 2. TicketNFT 배포 (없는 경우만)
    if (!contracts.TicketNFT) {
      console.log("\n[2/7] Deploying TicketNFT...");
      const TicketNFT = await hre.ethers.getContractFactory("TicketNFT");
      const ticketNFT = await TicketNFT.deploy(contracts.TicketAccessControl);
      await ticketNFT.waitForDeployment();
      contracts.TicketNFT = await ticketNFT.getAddress();
      console.log("✅ TicketNFT:", contracts.TicketNFT);
    } else {
      console.log("\n[2/7] TicketNFT already deployed:", contracts.TicketNFT);
    }

    // 3. EventManager 배포 (없는 경우만)
    if (!contracts.EventManager) {
      console.log("\n[3/7] Deploying EventManager...");
      const EventManager = await hre.ethers.getContractFactory("EventManager");
      const eventManager = await EventManager.deploy(
        contracts.TicketAccessControl,
        contracts.TicketNFT
      );
      await eventManager.waitForDeployment();
      contracts.EventManager = await eventManager.getAddress();
      console.log("✅ EventManager:", contracts.EventManager);
    } else {
      console.log("\n[3/7] EventManager already deployed:", contracts.EventManager);
    }

    // 4. TicketMarketplace 배포 (없는 경우만)
    if (!contracts.TicketMarketplace) {
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
    } else {
      console.log("\n[4/7] TicketMarketplace already deployed:", contracts.TicketMarketplace);
    }

    // 5. RefundManager 배포 (없는 경우만)
    if (!contracts.RefundManager) {
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
    } else {
      console.log("\n[5/7] RefundManager already deployed:", contracts.RefundManager);
    }

    // 6. SmartWallet 구현 배포 (없는 경우만)
    if (!contracts.SmartWallet) {
      console.log("\n[6/7] Deploying SmartWallet implementation...");
      const SmartWallet = await hre.ethers.getContractFactory("SmartWallet");
      const smartWallet = await SmartWallet.deploy(ENTRY_POINT_ADDRESS);
      await smartWallet.waitForDeployment();
      contracts.SmartWallet = await smartWallet.getAddress();
      console.log("✅ SmartWallet:", contracts.SmartWallet);
    } else {
      console.log("\n[6/7] SmartWallet already deployed:", contracts.SmartWallet);
    }

    // 7. SmartWalletFactory 배포 (없는 경우만)
    if (!contracts.SmartWalletFactory) {
      console.log("\n[7/7] Deploying SmartWalletFactory...");
      const SmartWalletFactory = await hre.ethers.getContractFactory("SmartWalletFactory");
      const factory = await SmartWalletFactory.deploy(ENTRY_POINT_ADDRESS);
      await factory.waitForDeployment();
      contracts.SmartWalletFactory = await factory.getAddress();
      console.log("✅ SmartWalletFactory:", contracts.SmartWalletFactory);
    } else {
      console.log("\n[7/7] SmartWalletFactory already deployed:", contracts.SmartWalletFactory);
    }

    // 8. 권한 설정 (컨트랙트가 모두 배포된 경우만)
    if (contracts.TicketNFT && contracts.EventManager && contracts.RefundManager) {
      console.log("\n[8/8] Setting up roles...");
      
      const TicketNFT = await hre.ethers.getContractFactory("TicketNFT");
      const ticketNFT = await TicketNFT.attach(contracts.TicketNFT);
      
      // EventManager에 MINTER_ROLE 부여
      const MINTER_ROLE = await ticketNFT.MINTER_ROLE();
      const hasMinterRole = await ticketNFT.hasRole(MINTER_ROLE, contracts.EventManager);
      if (!hasMinterRole) {
        const tx1 = await ticketNFT.grantRole(MINTER_ROLE, contracts.EventManager);
        await tx1.wait();
        console.log("✅ Granted MINTER_ROLE to EventManager");
      } else {
        console.log("✅ EventManager already has MINTER_ROLE");
      }

      // RefundManager에 BURNER_ROLE 부여
      const BURNER_ROLE = await ticketNFT.BURNER_ROLE();
      const hasBurnerRole = await ticketNFT.hasRole(BURNER_ROLE, contracts.RefundManager);
      if (!hasBurnerRole) {
        const tx2 = await ticketNFT.grantRole(BURNER_ROLE, contracts.RefundManager);
        await tx2.wait();
        console.log("✅ Granted BURNER_ROLE to RefundManager");
      } else {
        console.log("✅ RefundManager already has BURNER_ROLE");
      }
    }

    // 배포 정보 저장
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

    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

    // 배포 요약 출력
    console.log("\n" + "=".repeat(60));
    console.log("🎉 배포 완료!");
    console.log("=".repeat(60));
    console.log("Network:", networkName);
    console.log("Deployer:", deployer.address);
    console.log("\n📋 Contract Addresses:");
    Object.keys(contracts).forEach(key => {
      console.log(`  ${key}:`, contracts[key]);
    });
    console.log("  EntryPoint:", ENTRY_POINT_ADDRESS);
    console.log("\n💾 Deployment info saved to:", deploymentFile);
    console.log("=".repeat(60));

  } catch (error) {
    console.error("\n❌ 배포 실패:", error);
    
    // 현재까지 배포된 정보 저장
    if (Object.keys(contracts).length > 0) {
      const deploymentInfo = {
        network: networkName,
        deployer: deployer.address,
        entryPoint: ENTRY_POINT_ADDRESS,
        contracts: contracts,
        timestamp: new Date().toISOString(),
        error: error.message,
      };
      fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
      console.log("\n💾 Partial deployment info saved to:", deploymentFile);
      console.log("다시 실행하면 이미 배포된 컨트랙트를 재사용합니다.");
    }
    
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

