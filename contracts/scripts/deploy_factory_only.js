const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * SmartWalletFactory만 배포
 */
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying SmartWalletFactory with the account:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "MATIC");
  
  if (balance === 0n) {
    console.error("❌ Error: Account balance is 0. Please fund your account first.");
    process.exit(1);
  }

  // ERC-4337 표준 EntryPoint 주소
  const ENTRY_POINT_ADDRESS = process.env.ENTRY_POINT_ADDRESS || 
    "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789";

  console.log("\n" + "=".repeat(60));
  console.log("🚀 SmartWalletFactory 배포 시작");
  console.log("=".repeat(60));
  console.log("Network:", hre.network.name);
  console.log("EntryPoint:", ENTRY_POINT_ADDRESS);

  try {
    // SmartWalletFactory 배포 (SmartWallet 구현 포함)
    console.log("\n[1/1] Deploying SmartWalletFactory...");
    const SmartWalletFactory = await hre.ethers.getContractFactory("SmartWalletFactory");
    const factory = await SmartWalletFactory.deploy(ENTRY_POINT_ADDRESS);
    await factory.waitForDeployment();
    const factoryAddress = await factory.getAddress();
    const smartWalletImpl = await factory.walletImplementation();
    
    console.log("\n" + "=".repeat(60));
    console.log("✅ SmartWalletFactory 배포 완료!");
    console.log("=".repeat(60));
    console.log("Network:", hre.network.name);
    console.log("Deployer:", deployer.address);
    console.log("\n📋 Contract Addresses:");
    console.log("  SmartWalletFactory:", factoryAddress);
    console.log("  SmartWallet (implementation):", smartWalletImpl);
    console.log("  EntryPoint:", ENTRY_POINT_ADDRESS);
    console.log("\n🔗 Explorer:");
    if (hre.network.name === "amoy") {
      console.log(`  Factory: https://amoy.polygonscan.com/address/${factoryAddress}`);
      console.log(`  SmartWallet: https://amoy.polygonscan.com/address/${smartWalletImpl}`);
    }
    console.log("=".repeat(60));

    // 배포 정보 저장
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

    deploymentInfo.network = networkName;
    deploymentInfo.deployer = deployer.address;
    deploymentInfo.entryPoint = ENTRY_POINT_ADDRESS;
    deploymentInfo.contracts = deploymentInfo.contracts || {};
    deploymentInfo.contracts.SmartWalletFactory = factoryAddress;
    deploymentInfo.contracts.SmartWallet = smartWalletImpl;
    deploymentInfo.timestamp = new Date().toISOString();

    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
    console.log("\n💾 Deployment info saved to:", deploymentFile);

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

