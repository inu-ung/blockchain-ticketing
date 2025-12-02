const hre = require("hardhat");
const fs = require("fs");

async function main() {
  const network = hre.network.name;
  const deploymentFile = `deployments/${network}.json`;

  if (!fs.existsSync(deploymentFile)) {
    console.error(`Deployment file not found: ${deploymentFile}`);
    console.log("Please deploy contracts first.");
    process.exit(1);
  }

  const deployment = JSON.parse(fs.readFileSync(deploymentFile, "utf8"));
  const contracts = deployment.contracts;

  console.log(`\nVerifying contracts on ${network}...\n`);

  // 1. TicketAccessControl 검증
  console.log("1. Verifying TicketAccessControl...");
  try {
    await hre.run("verify:verify", {
      address: contracts.TicketAccessControl,
      constructorArguments: [deployment.deployer],
    });
    console.log("✅ TicketAccessControl verified\n");
  } catch (error) {
    console.log("❌ TicketAccessControl verification failed:", error.message, "\n");
  }

  // 2. TicketNFT 검증
  console.log("2. Verifying TicketNFT...");
  try {
    await hre.run("verify:verify", {
      address: contracts.TicketNFT,
      constructorArguments: [deployment.deployer],
    });
    console.log("✅ TicketNFT verified\n");
  } catch (error) {
    console.log("❌ TicketNFT verification failed:", error.message, "\n");
  }

  // 3. EventManager 검증
  console.log("3. Verifying EventManager...");
  try {
    await hre.run("verify:verify", {
      address: contracts.EventManager,
      constructorArguments: [
        contracts.TicketAccessControl,
        contracts.TicketNFT,
      ],
    });
    console.log("✅ EventManager verified\n");
  } catch (error) {
    console.log("❌ EventManager verification failed:", error.message, "\n");
  }

  // 4. TicketMarketplace 검증
  console.log("4. Verifying TicketMarketplace...");
  try {
    await hre.run("verify:verify", {
      address: contracts.TicketMarketplace,
      constructorArguments: [
        contracts.TicketAccessControl,
        contracts.TicketNFT,
        contracts.EventManager,
        deployment.deployer, // feeRecipient
      ],
    });
    console.log("✅ TicketMarketplace verified\n");
  } catch (error) {
    console.log("❌ TicketMarketplace verification failed:", error.message, "\n");
  }

  // 5. RefundManager 검증
  console.log("5. Verifying RefundManager...");
  try {
    await hre.run("verify:verify", {
      address: contracts.RefundManager,
      constructorArguments: [
        contracts.TicketAccessControl,
        contracts.TicketNFT,
        contracts.EventManager,
      ],
    });
    console.log("✅ RefundManager verified\n");
  } catch (error) {
    console.log("❌ RefundManager verification failed:", error.message, "\n");
  }

  console.log("Verification complete!");
  console.log("\nView contracts on explorer:");
  if (network === "mumbai") {
    console.log(`https://mumbai.polygonscan.com/address/${contracts.TicketAccessControl}`);
  } else if (network === "polygon") {
    console.log(`https://polygonscan.com/address/${contracts.TicketAccessControl}`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

