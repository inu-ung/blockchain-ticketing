const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());

  // 1. AccessControl 배포
  console.log("\n1. Deploying TicketAccessControl...");
  const TicketAccessControl = await hre.ethers.getContractFactory("TicketAccessControl");
  const accessControl = await TicketAccessControl.deploy(deployer.address);
  await accessControl.waitForDeployment();
  const accessControlAddress = await accessControl.getAddress();
  console.log("TicketAccessControl deployed to:", accessControlAddress);

  // 2. TicketNFT 배포
  console.log("\n2. Deploying TicketNFT...");
  const TicketNFT = await hre.ethers.getContractFactory("TicketNFT");
  const ticketNFT = await TicketNFT.deploy(deployer.address);
  await ticketNFT.waitForDeployment();
  const ticketNFTAddress = await ticketNFT.getAddress();
  console.log("TicketNFT deployed to:", ticketNFTAddress);

  // 3. EventManager 배포
  console.log("\n3. Deploying EventManager...");
  const EventManager = await hre.ethers.getContractFactory("EventManager");
  const eventManager = await EventManager.deploy(accessControlAddress, ticketNFTAddress);
  await eventManager.waitForDeployment();
  const eventManagerAddress = await eventManager.getAddress();
  console.log("EventManager deployed to:", eventManagerAddress);

  // 4. TicketMarketplace 배포
  console.log("\n4. Deploying TicketMarketplace...");
  const TicketMarketplace = await hre.ethers.getContractFactory("TicketMarketplace");
  const marketplace = await TicketMarketplace.deploy(
    accessControlAddress,
    ticketNFTAddress,
    eventManagerAddress,
    deployer.address // feeRecipient
  );
  await marketplace.waitForDeployment();
  const marketplaceAddress = await marketplace.getAddress();
  console.log("TicketMarketplace deployed to:", marketplaceAddress);

  // 5. RefundManager 배포
  console.log("\n5. Deploying RefundManager...");
  const RefundManager = await hre.ethers.getContractFactory("RefundManager");
  const refundManager = await RefundManager.deploy(
    accessControlAddress,
    ticketNFTAddress,
    eventManagerAddress
  );
  await refundManager.waitForDeployment();
  const refundManagerAddress = await refundManager.getAddress();
  console.log("RefundManager deployed to:", refundManagerAddress);

  // 6. 권한 설정
  console.log("\n6. Setting up roles...");
  
  // EventManager에 MINTER_ROLE 부여
  const MINTER_ROLE = await ticketNFT.MINTER_ROLE();
  const tx1 = await ticketNFT.grantRole(MINTER_ROLE, eventManagerAddress);
  await tx1.wait();
  console.log("Granted MINTER_ROLE to EventManager");

  // RefundManager에 BURNER_ROLE 부여
  const BURNER_ROLE = await ticketNFT.BURNER_ROLE();
  const tx2 = await ticketNFT.grantRole(BURNER_ROLE, refundManagerAddress);
  await tx2.wait();
  console.log("Granted BURNER_ROLE to RefundManager");

  // 배포 정보 출력
  console.log("\n=== Deployment Summary ===");
  console.log("Network:", hre.network.name);
  console.log("Deployer:", deployer.address);
  console.log("\nContract Addresses:");
  console.log("TicketAccessControl:", accessControlAddress);
  console.log("TicketNFT:", ticketNFTAddress);
  console.log("EventManager:", eventManagerAddress);
  console.log("TicketMarketplace:", marketplaceAddress);
  console.log("RefundManager:", refundManagerAddress);

  // 배포 정보를 파일로 저장
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
    deployer: deployer.address,
    contracts: {
      TicketAccessControl: accessControlAddress,
      TicketNFT: ticketNFTAddress,
      EventManager: eventManagerAddress,
      TicketMarketplace: marketplaceAddress,
      RefundManager: refundManagerAddress,
    },
    timestamp: new Date().toISOString(),
  };

  fs.writeFileSync(
    `deployments/${hre.network.name}.json`,
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\nDeployment info saved to deployments/" + hre.network.name + ".json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

