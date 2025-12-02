const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * TicketNFT만 배포
 */
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying TicketNFT with the account:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "MATIC");
  
  if (balance === 0n) {
    console.error("❌ Error: Account balance is 0. Please fund your account first.");
    process.exit(1);
  }

  console.log("\n" + "=".repeat(60));
  console.log("🚀 TicketNFT 배포 시작");
  console.log("=".repeat(60));
  console.log("Network:", hre.network.name);

  try {
    // TicketNFT 배포
    console.log("\n[1/1] Deploying TicketNFT...");
    const TicketNFT = await hre.ethers.getContractFactory("TicketNFT");
    const ticketNFT = await TicketNFT.deploy(deployer.address);
    await ticketNFT.waitForDeployment();
    const ticketNFTAddress = await ticketNFT.getAddress();
    
    console.log("\n" + "=".repeat(60));
    console.log("✅ TicketNFT 배포 완료!");
    console.log("=".repeat(60));
    console.log("Network:", hre.network.name);
    console.log("Deployer:", deployer.address);
    console.log("\n📋 Contract Address:");
    console.log("  TicketNFT:", ticketNFTAddress);
    console.log("\n🔗 Explorer:");
    if (hre.network.name === "amoy") {
      console.log(`  https://amoy.polygonscan.com/address/${ticketNFTAddress}`);
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
    deploymentInfo.contracts = deploymentInfo.contracts || {};
    deploymentInfo.contracts.TicketNFT = ticketNFTAddress;
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

