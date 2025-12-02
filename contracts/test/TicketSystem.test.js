const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Ticket System", function () {
  let accessControl;
  let ticketNFT;
  let eventManager;
  let marketplace;
  let refundManager;

  let admin;
  let organizer;
  let buyer1;
  let buyer2;

  beforeEach(async function () {
    [admin, organizer, buyer1, buyer2] = await ethers.getSigners();

    // 1. AccessControl 배포
    const TicketAccessControl = await ethers.getContractFactory("TicketAccessControl");
    accessControl = await TicketAccessControl.deploy(admin.address);
    await accessControl.waitForDeployment();

    // 2. TicketNFT 배포
    const TicketNFT = await ethers.getContractFactory("TicketNFT");
    ticketNFT = await TicketNFT.deploy(admin.address);
    await ticketNFT.waitForDeployment();

    // 3. EventManager 배포
    const EventManager = await ethers.getContractFactory("EventManager");
    eventManager = await EventManager.deploy(
      await accessControl.getAddress(),
      await ticketNFT.getAddress()
    );
    await eventManager.waitForDeployment();

    // 4. Marketplace 배포
    const TicketMarketplace = await ethers.getContractFactory("TicketMarketplace");
    marketplace = await TicketMarketplace.deploy(
      await accessControl.getAddress(),
      await ticketNFT.getAddress(),
      await eventManager.getAddress(),
      admin.address // feeRecipient
    );
    await marketplace.waitForDeployment();

    // 5. RefundManager 배포
    const RefundManager = await ethers.getContractFactory("RefundManager");
    refundManager = await RefundManager.deploy(
      await accessControl.getAddress(),
      await ticketNFT.getAddress(),
      await eventManager.getAddress()
    );
    await refundManager.waitForDeployment();

    // 권한 설정
    const MINTER_ROLE = await ticketNFT.MINTER_ROLE();
    await ticketNFT.grantRole(MINTER_ROLE, await eventManager.getAddress());

    const BURNER_ROLE = await ticketNFT.BURNER_ROLE();
    await ticketNFT.grantRole(BURNER_ROLE, await refundManager.getAddress());

    // 주최자 역할 부여
    await accessControl.addOrganizer(organizer.address);
  });

  describe("AccessControl", function () {
    it("Should set admin correctly", async function () {
      expect(await accessControl.hasRole(await accessControl.ADMIN_ROLE(), admin.address)).to.be.true;
    });

    it("Should add organizer", async function () {
      await accessControl.addOrganizer(organizer.address);
      expect(await accessControl.isOrganizer(organizer.address)).to.be.true;
    });
  });

  describe("EventManager", function () {
    it("Should create an event", async function () {
      const ipfsHash = "QmTest123";
      const price = ethers.parseEther("0.1");
      const maxTickets = 100;
      const startTime = Math.floor(Date.now() / 1000) + 3600; // 1시간 후
      const endTime = Math.floor(Date.now() / 1000) + 7200; // 2시간 후
      const eventDate = Math.floor(Date.now() / 1000) + 86400; // 1일 후

      const tx = await eventManager
        .connect(organizer)
        .createEvent(ipfsHash, price, maxTickets, startTime, endTime, eventDate);

      await expect(tx)
        .to.emit(eventManager, "EventCreated")
        .withArgs(0, organizer.address, ipfsHash, price, maxTickets);

      // 이벤트 정보 확인 (개별 필드로 접근)
      // 이벤트 정보 확인 (개별 함수 사용)
      expect(await eventManager.getEventOrganizer(0)).to.equal(organizer.address);
      expect(await eventManager.getEventPrice(0)).to.equal(price);
      expect(await eventManager.getEventMaxTickets(0)).to.equal(maxTickets);
    });

    it("Should approve event", async function () {
      // 이벤트 생성
      const ipfsHash = "QmTest123";
      const price = ethers.parseEther("0.1");
      const maxTickets = 100;
      const startTime = Math.floor(Date.now() / 1000) + 3600;
      const endTime = Math.floor(Date.now() / 1000) + 7200;
      const eventDate = Math.floor(Date.now() / 1000) + 86400;

      await eventManager
        .connect(organizer)
        .createEvent(ipfsHash, price, maxTickets, startTime, endTime, eventDate);

      // 이벤트 승인
      const tx = await eventManager.connect(admin).approveEvent(0);
      await expect(tx)
        .to.emit(eventManager, "EventApproved")
        .withArgs(0, admin.address);

      expect(await eventManager.getEventApproved(0)).to.be.true;
    });

    it("Should purchase ticket", async function () {
      // 이벤트 생성 및 승인
      const ipfsHash = "QmTest123";
      const price = ethers.parseEther("0.1");
      const maxTickets = 100;
      const now = Math.floor(Date.now() / 1000);
      const startTime = now - 3600; // 1시간 전
      const endTime = now + 3600; // 1시간 후
      const eventDate = now + 86400; // 1일 후

      await eventManager
        .connect(organizer)
        .createEvent(ipfsHash, price, maxTickets, startTime, endTime, eventDate);

      await eventManager.connect(admin).approveEvent(0);

      // 티켓 구매
      const tokenURI = "ipfs://QmTicket123";
      const tx = await eventManager
        .connect(buyer1)
        .purchaseTicket(0, tokenURI, { value: price });

      await expect(tx)
        .to.emit(eventManager, "TicketSold")
        .withArgs(0, 0, buyer1.address, price);

      // 티켓 소유권 확인
      expect(await ticketNFT.ownerOf(0)).to.equal(buyer1.address);
      expect(await ticketNFT.tokenToEvent(0)).to.equal(0);
    });
  });

  describe("TicketMarketplace", function () {
    beforeEach(async function () {
      // 이벤트 생성 및 승인
      const ipfsHash = "QmTest123";
      const price = ethers.parseEther("0.1");
      const maxTickets = 100;
      const now = Math.floor(Date.now() / 1000);
      const startTime = now - 3600;
      const endTime = now + 3600;
      const eventDate = now + 86400;

      await eventManager
        .connect(organizer)
        .createEvent(ipfsHash, price, maxTickets, startTime, endTime, eventDate);

      await eventManager.connect(admin).approveEvent(0);

      // 티켓 구매
      const tokenURI = "ipfs://QmTicket123";
      await eventManager
        .connect(buyer1)
        .purchaseTicket(0, tokenURI, { value: price });

    });

    it("Should list ticket for resale", async function () {
      // 마켓플레이스에 전송 권한 부여
      await ticketNFT.connect(buyer1).approve(await marketplace.getAddress(), 0);
      const resalePrice = ethers.parseEther("0.15");

      const tx = await marketplace
        .connect(buyer1)
        .listTicketForResale(0, resalePrice);

      await expect(tx)
        .to.emit(marketplace, "TicketListed")
        .withArgs(0, buyer1.address, resalePrice);

      const listing = await marketplace.getListing(0);
      expect(listing.active).to.be.true;
      expect(listing.price).to.equal(resalePrice);
      expect(listing.seller).to.equal(buyer1.address);
    });

    it("Should buy resale ticket", async function () {
      const resalePrice = ethers.parseEther("0.15");

      // 마켓플레이스에 전송 권한 부여
      await ticketNFT.connect(buyer1).approve(await marketplace.getAddress(), 0);

      // 재판매 등록
      await marketplace
        .connect(buyer1)
        .listTicketForResale(0, resalePrice);

      // 재판매 구매
      const tx = await marketplace
        .connect(buyer2)
        .buyResaleTicket(0, { value: resalePrice });

      await expect(tx)
        .to.emit(marketplace, "TicketSold");

      // 소유권 확인
      expect(await ticketNFT.ownerOf(0)).to.equal(buyer2.address);
    });

    it("Should enforce max price", async function () {
      // 마켓플레이스에 전송 권한 부여
      await ticketNFT.connect(buyer1).approve(await marketplace.getAddress(), 0);

      const eventPrice = await eventManager.getEventPrice(0);
      const maxPrice = (eventPrice * 20000n) / 10000n; // 200%
      const invalidPrice = maxPrice + ethers.parseEther("0.01");

      await expect(
        marketplace
          .connect(buyer1)
          .listTicketForResale(0, invalidPrice)
      ).to.be.revertedWith("TicketMarketplace: price exceeds maximum");
    });
  });

  describe("RefundManager", function () {
    beforeEach(async function () {
      // 이벤트 생성 및 승인
      const ipfsHash = "QmTest123";
      const price = ethers.parseEther("0.1");
      const maxTickets = 100;
      const now = Math.floor(Date.now() / 1000);
      const startTime = now - 3600;
      const endTime = now + 3600;
      const eventDate = now + 86400 * 8; // 8일 후 (환불 기간 내)

      await eventManager
        .connect(organizer)
        .createEvent(ipfsHash, price, maxTickets, startTime, endTime, eventDate);

      await eventManager.connect(admin).approveEvent(0);

      // 티켓 구매
      const tokenURI = "ipfs://QmTicket123";
      await eventManager
        .connect(buyer1)
        .purchaseTicket(0, tokenURI, { value: price });
    });

    it("Should request refund", async function () {
      const tx = await refundManager
        .connect(buyer1)
        .requestRefund(0);

      await expect(tx)
        .to.emit(refundManager, "RefundRequested");

      const request = await refundManager.getRefundRequest(0);
      expect(request.requester).to.equal(buyer1.address);
      expect(request.processed).to.be.false;
    });

    it("Should process refund", async function () {
      // 환불 요청
      await refundManager
        .connect(buyer1)
        .requestRefund(0);

      // RefundManager에 환불 금액 전송 (실제로는 주최자가 보유)
      // 주최자가 RefundManager에 이더를 전송할 수 있도록 receive 함수가 필요
      // 대신 주최자가 직접 환불 금액을 보유하고 있어야 함
      // 테스트를 위해 RefundManager에 이더 전송
      const refundPrice = ethers.parseEther("0.1");
      await admin.sendTransaction({
        to: await refundManager.getAddress(),
        value: refundPrice,
      });

      // 환불 처리
      const tx = await refundManager
        .connect(organizer)
        .processRefund(0);

      await expect(tx)
        .to.emit(refundManager, "RefundProcessed");

      // 티켓 소각 확인
      await expect(ticketNFT.ownerOf(0)).to.be.reverted;
    });
  });
});

