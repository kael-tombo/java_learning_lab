# Blockchain Security - MINI PROJECT

## Project: VaultAudit — exploit, fix, and verify a vault-style smart contract

Write a Solidity vault with three deliberate vulnerabilities, exploit each on a local chain,
fix them properly, and add invariant/fuzz tests that would have caught each one.

### Architecture

```
  VULNERABLE (v1)                      FIXED (v2)
  ──────────────                       ──────────
  withdraw(): external call before       checks-effects-interactions ordering
    state update  -> reentrancy         ReentrancyGuard on all state-mutating fns
                                       (or: state updated first, then transfer)

  onlyOwner single key                  role-based access + 2-of-3 multisig
                                       + 48h timelock on upgrades

  price = oracle.latest()               TWAP over a window, staleness check,
    (single spot read)                   circuit breaker on deviation

  int256 amount * 1e18                  unchecked / full-precision mulDiv,
    (overflow-prone)                     Solidity 0.8 checked arithmetic
```

### Implementation

The vulnerable version, annotated with the three bugs:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.6;   // NOTE: pre-0.8 - arithmetic is UNCHECKED. Bug 3.

contract VaultV1 {
    mapping(address => uint256) public balances;
    IERC20 public token;
    uint256 public totalShares;
    address public owner;

    // BUG 1: no access control at all. Anyone can drain the fee pool.
    function setFee(uint256 newFee) external { fee = newFee; }

    // BUG 2: reentrancy. The external call happens BEFORE balances is decremented,
    // so an attacker contract re-enters and drains more than they deposited.
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "insufficient");
        token.transfer(msg.sender, amount);      // <-- external call, state not yet updated
        balances[msg.sender] -= amount;          // <-- too late
    }

    // BUG 3: spot oracle read, manipulable within a single block via flash loan.
    function convertToToken(uint256 shares) public view returns (uint256) {
        return shares * oracle.latestPrice() / 1e18;
    }
}
```

The exploit contracts, one per vulnerability:

```solidity
// Exploit 2: reentrancy
contract ReentrancyExploit {
    VaultV1 public vault;
    uint256 public count;
    constructor(VaultV1 _v) { vault = _v; }

    function attack(uint256 amount) external {
        vault.deposit(amount);
    }

    // Each call re-enters before the victim's state update lands.
    receive() external { if (count < 20) { count++; uint256 bal = vault.balances(address(this)); vault.withdraw(bal); } }
}

contract OwnershipExploit {
    function run(VaultV1 v) external { v.setFee(0); v.drainTo(msg.sender); }  // bug 1, no guard
}
```

The fixed version:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;   // checked arithmetic by default - fixes bug 3's overflow class

contract VaultV2 {
    // FIX 2: a reentrancy guard on every function that sends tokens.
    uint256 private _entered = 1;
    modifier nonReentrant() {
        require(_entered == 1, "reentrant");
        _entered = 2;
        _;
        _entered = 1;
    }

    // FIX 1: role-based access with a multisig, plus a timelock for parameter changes.
    bytes32 public constant ADMIN = keccak256("ADMIN");
    mapping(address => bytes32) public roles;
    uint256 public constant TIMELOCK = 48 hours;
    mapping(bytes32 => uint256) public pendingChangeAt;

    function proposeFee(uint256 newFee) external onlyRole(ADMIN) {
        pendingChangeAt[keccak256("fee")] = block.timestamp + TIMELOCK;   // visible, delayed
        pendingFee = newFee;
    }
    function executeFee() external {
        require(block.timestamp >= pendingChangeAt[keccak256("fee")], "timelock active");
        require(pendingChangeAt[keccak256("fee")] != 0, "none pending");
        fee = pendingFee;                                                 // clear first
        pendingChangeAt[keccak256("fee")] = 0;
    }

    // FIX 2: checks-effects-interactions. State changes BEFORE the external call.
    function withdraw(uint256 amount) external nonReentrant {
        require(balances[msg.sender] >= amount, "insufficient");
        balances[msg.sender] -= amount;      // effect first
        totalShares -= amount;
        emit Withdrawn(msg.sender, amount);
        token.transfer(msg.sender, amount);  // interaction last
    }

    // FIX 3: manipulation-resistant pricing. TWAP + staleness + deviation circuit breaker.
    function convertToToken(uint256 shares) public view returns (uint256) {
        (uint256 twap, bool ok) = oracle.twap(WINDOW);
        require(ok && block.timestamp - oracle.lastUpdate() <= MAX_STALENESS, "stale oracle");
        uint256 out = FullMath.mulDiv(shares, twap, 1e18);
        uint256 dev = (out * fee) / 10000;
        require(out - dev <= perTxMax, "exceeds per-tx cap");   // blast-radius limiter
        return out - dev;
    }
}
```

Invariants and fuzz tests, which catch what example-based tests miss:

```solidity
contract VaultV2Invariant is Test {
    VaultV2 vault; address actor;

    /// @custom:invariant No free money: total assets >= sum of claimable balances.
    function invariant_solvency() public view {
        uint256 total = 0;
        address[] memory actors = actors();
        for (uint i = 0; i < actors.length; i++) total += vault.convertToToken(vault.balancesOf(actors[i]));
        assertGe(vault.totalAssets(), total, "vault is insolvent");
    }

    /// @custom:invariant A reentrant caller cannot extract more than it deposited.
    function invariant_noReentrancyProfit() public { ... }

    function testFuzz_depositWithdrawRoundTrip(uint96 amount) public {
        uint256 a = bound(amount, 1, type(uint96).max);
        vm.prank(actor);
        vault.deposit(a);
        vm.prank(actor);
        vault.withdraw(a);
        assertEq(vault.balancesOf(actor), 0);
    }
}
```

### Test It

```javascript
// hardhat/foundry tests - each exploit FAILS on V2 and SUCCEEDS on V1
it("reentrancy drains V1", async () => {
  await vaultV1.deposit(parseEther("1")); { await vaultV1.setOracle(manipulableOracle); }
  const balBefore = await token.balanceOf(attacker.address);
  await attacker.attack();            // withdraws 20x its deposit
  expect(await token.balanceOf(attacker.address)).to.be.gt(balBefore * 10n);
});

it("reentrancy exploit FAILS against V2", async () => {
  await expect(attacker2.attack()).to.be.revertedWith("reentrant");
});

it("flash-loan price manipulation is bounded by the circuit breaker", async () => {
  await oracle.manipulate();                                     // single-block spike
  await expect(vaultV2.convertToToken(parseEther("1"))).to.be.revertedWith("exceeds per-tx cap");
});

it("fee change requires the timelock", async () => {
  await vaultV2.proposeFee(500);
  await expect(vaultV2.executeFee()).to.be.revertedWith("timelock active");
  await vm.warp(block.timestamp + 48 hours);
  await vaultV2.executeFee();
  expect(await vaultV2.fee()).to.equal(500);
});
```

### Deliverables

- [ ] `VaultV1` with three annotated vulnerabilities (access, reentrancy, oracle)
- [ ] Three working exploit contracts demonstrating each bug on a local chain
- [ ] `VaultV2` fixes: role-based access + multisig, `nonReentrant` + CEI, TWAP + circuit breaker
- [ ] Invariant tests: solvency, no reentrancy profit, fee accounting
- [ ] Fuzz tests for deposit/withdraw round-trips and fee boundaries
- [ ] Timelock tests proving parameter changes cannot be instant
- [ ] Gas/size report and a NatSpec comment block on every external function
- [ ] `AUDIT_NOTES.md` listing residual risks and what an external audit should prioritise
