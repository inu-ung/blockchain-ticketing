const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Granting roles with account:", deployer.address);
  
  // 배포 정보 로드
  const fs = require("fs");
  const deploymentInfo = JSON.parse(fs.readFileSync("deployments/localhost.json", "utf8"));
  
  const accessControlAddress = deploymentInfo.contracts.TicketAccessControl;
  const AccessControl = await hre.ethers.getContractFactory("TicketAccessControl");
  const accessControl = AccessControl.attach(accessControlAddress);
  
  // 서비스 계정 주소 (백엔드에서 사용하는 계정)
  const serviceAccount = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266";
  
  // ORGANIZER_ROLE 부여
  const ORGANIZER_ROLE = await accessControl.ORGANIZER_ROLE();
  const tx1 = await accessControl.addOrganizer(serviceAccount);
  await tx1.wait();
  console.log("✅ Granted ORGANIZER_ROLE to", serviceAccount);
  
  // ADMIN_ROLE 부여
  const ADMIN_ROLE = await accessControl.ADMIN_ROLE();
  const tx2 = await accessControl.addAdmin(serviceAccount);
  await tx2.wait();
  console.log("✅ Granted ADMIN_ROLE to", serviceAccount);
  
  // 확인
  const isOrganizer = await accessControl.isOrganizer(serviceAccount);
  const isAdmin = await accessControl.isAdmin(serviceAccount);
  console.log("\n✅ Verification:");
  console.log("  Is Organizer:", isOrganizer);
  console.log("  Is Admin:", isAdmin);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
