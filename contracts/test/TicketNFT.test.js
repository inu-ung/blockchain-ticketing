const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TicketNFT", function () {
  let ticketNFT;
  let admin;
  let minter;
  let user;

  beforeEach(async function () {
    [admin, minter, user] = await ethers.getSigners();

    // TicketNFT 배포
    const TicketNFT = await ethers.getContractFactory("TicketNFT");
    ticketNFT = await TicketNFT.deploy(admin.address);
    await ticketNFT.waitForDeployment();

    // Minter 역할 부여
    const MINTER_ROLE = await ticketNFT.MINTER_ROLE();
    await ticketNFT.grantRole(MINTER_ROLE, minter.address);
  });

  describe("Deployment", function () {
    it("Should set admin correctly", async function () {
      const DEFAULT_ADMIN_ROLE = await ticketNFT.DEFAULT_ADMIN_ROLE();
      expect(await ticketNFT.hasRole(DEFAULT_ADMIN_ROLE, admin.address)).to.be.true;
    });

    it("Should grant MINTER_ROLE to minter", async function () {
      const MINTER_ROLE = await ticketNFT.MINTER_ROLE();
      expect(await ticketNFT.hasRole(MINTER_ROLE, minter.address)).to.be.true;
    });
  });

  describe("Minting", function () {
    it("Should mint ticket successfully", async function () {
      const eventId = 1;
      const tokenURI = "ipfs://QmTest123";

      await expect(
        ticketNFT.connect(minter).mintTicket(user.address, eventId, tokenURI)
      )
        .to.emit(ticketNFT, "TicketMinted")
        .withArgs(0, eventId, user.address, tokenURI);

      expect(await ticketNFT.ownerOf(0)).to.equal(user.address);
      expect(await ticketNFT.tokenURI(0)).to.equal(tokenURI);
      expect(await ticketNFT.tokenToEvent(0)).to.equal(eventId);
    });

    it("Should revert if non-minter tries to mint", async function () {
      await expect(
        ticketNFT.connect(user).mintTicket(user.address, 1, "ipfs://test")
      ).to.be.revertedWithCustomError(ticketNFT, "AccessControlUnauthorizedAccount");
    });
  });

  describe("Burning", function () {
    beforeEach(async function () {
      // 티켓 발행
      await ticketNFT.connect(minter).mintTicket(user.address, 1, "ipfs://test");
      
      // BURNER_ROLE 부여
      const BURNER_ROLE = await ticketNFT.BURNER_ROLE();
      await ticketNFT.grantRole(BURNER_ROLE, minter.address);
    });

    it("Should burn ticket successfully", async function () {
      await expect(
        ticketNFT.connect(minter).burnTicket(0)
      )
        .to.emit(ticketNFT, "TicketBurned")
        .withArgs(0);

      await expect(ticketNFT.ownerOf(0)).to.be.reverted;
    });

    it("Should revert if non-burner tries to burn", async function () {
      await expect(
        ticketNFT.connect(user).burnTicket(0)
      ).to.be.revertedWithCustomError(ticketNFT, "AccessControlUnauthorizedAccount");
    });
  });
});

