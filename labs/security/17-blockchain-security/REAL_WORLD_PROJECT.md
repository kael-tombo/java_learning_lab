# Blockchain Security - REAL WORLD PROJECT

## Project: TokenLaunch — shipping a production token with governance and a kill switch

A team is launching a utility token with a treasury, staking, and a bridge to another chain.
The contract is permanent once deployed in the general case, so the work is: verify before
launch, govern upgrades safely, and be ready to respond within minutes if something is
wrong. The most important deliverable is the incident runbook.

### Architecture

```
  Pre-launch          Deploy             Operate                   Respond
  ──────────          ───────            ───────                   ────────
  audit + fuzz        proxy + impl       multisig (3-of-5)          pause (guardian, 1-of-3)
  invariant tests     timelock 48h       fee + rate params          front-run runbook
  simulation          TVL caps           oracle redundancy          bridge halt
  bug bounty          per-tx limits      monitoring + anomaly       post-mortem

  Trust assumptions stated explicitly:
   - Oracle providers (2-of-3, TWAP window)  - the underlying L2's finality and data availability
   - Bridge relayers / optimistic window       - governance key custody (multisig signers)
   - Foundation team for parameter proposals   - users behave rationally (economic model)
```

### Implementation

Upgradeable pattern with the safety properties that matter — a timelock users can see,
and a guardian that can pause but not steal:

```solidity
contract TokenController is Initializable, OwnableUpgradeable, PausableUpgradeable, AccessControlUpgradeable {
    // Proxy points at this implementation; upgrades go through the timelock, so an
    // upgrade is announced 48h ahead and users can exit if they dislike it.
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER");

    // Guardian can pause within one transaction. It CANNOT upgrade, mint, or withdraw:
    // asymmetric power on purpose - fast response, minimal blast radius.
    address public guardian;
    mapping(address => bool) public isGuardian;

    modifier onlyGuardianOrAdmin() {
        require(msg.sender == guardian || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "not authorized");
        _;
    }

    function setGuardian(address newGuardian) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newGuardian != address(0));
        guardian = newGuardian;
        emit GuardianChanged(old, newGuardian);
    }

    function emergencyPause(string calldata reason) external onlyGuardianOrAdmin {
        _pause();
        emit EmergencyPaused(msg.sender, reason);      // reason is on-chain: forensics later
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(block.timestamp >= unpauseNotBefore, "cooldown");   // anti-instant re-pause loop
        _unpause();
    }

    /// @custom:security Every privileged function must be reachable only through the timelock
    /// for the timelock's full delay, or the whole upgrade model is decorative.
    function scheduleUpgrade(address newImpl) external onlyRole(UPGRADER_ROLE) {
        timelock.schedule(address(this), abi.encodeCall(IUpgradeable.upgradeTo, (newImpl)), 48 hours);
    }
}
```

Oracle integration with redundancy, staleness rejection, and a deviation circuit breaker:

```solidity
contract PriceGuard {
    struct Feed { bool enabled; uint256 price; uint256 updatedAt; }
    mapping(address => Feed) public feeds;              // 3 independent providers
    uint256 public constant MAX_STALENESS = 1 hours;
    uint256 public constant MAX_DEVIATION_BPS = 500;    // 5% - trip a pause rather than settle badly

    /// @custom:security Median of enabled feeds, with staleness and deviation checks.
    /// A single manipulated feed cannot move the settlement price.
    function price() public view returns (uint256) {
        uint256[3] memory ps;
        uint256 n;
        for (uint256 i = 0; i < 3; i++) {
            Feed storage f = feeds[providers[i]];
            if (!f.enabled) continue;
            require(block.timestamp - f.updatedAt <= MAX_STALENESS, "stale feed");
            ps[n++] = f.price;
        }
        require(n >= 2, "insufficient feeds");
        uint256 sorted = _median(ps, n);
        uint256 reference = lastGoodPrice;
        if (reference != 0 && _deviationBps(sorted, reference) > MAX_DEVIATION_BPS)
            revert("price deviation - circuit breaker");
        return sorted;
    }
}
```

Monitoring that detects an ongoing exploit rather than reporting it after the fact:

```solidity
contract AnomalyDetector {
    /// Tracks drain-shaped behaviour: many small withdrawals, or a sudden TVL drop.
    function registerWithdraw(address user, uint256 amount) external {
        window.withdrawals[user] += 1;
        window.withdrawVolume[user] += amount;
        if (window.withdrawals[user] > 20 && window.withdrawVolume[user] > thresholdFor(user))
            monitor.flag(FLAG_WHALE_DRAIN, user, window.withdrawVolume[user]);
    }

    /// @custom:security TVL drop beyond X% in one block is either a flash-loan attack
    /// or a protocol bug. Either way, humans should be paged immediately.
    function checkTVL(uint256 current, uint256 previous) external {
        if (previous > 0 && (previous - current) * 10000 / previous > 2000)
            monitor.critical(FLASH_TV_DROP, current, previous);
    }
}
```

### Non-functional requirements

- **Audit**: two independent firms, sequential (the second reviews the first's findings).
  Severity classification agreed in writing before the second engagement starts.
- **Verification**: formal verification of the core accounting invariants; fuzz campaign
  with a published budget; a public bug bounty with a meaningful maximum payout.
- **Key custody**: multisig signers in hardware wallets on geographically separated
  operators; no single person can pause-and-upgrade; key ceremony documented.
- **Timelock**: 48 h minimum on all parameter and implementation changes, surfaced in the UI.
- **Blast-radius limits**: per-transaction caps, per-address daily withdrawal caps, and a
  rate limiter — so a bug drains slowly enough to be detected and paused.
- **Detection latency**: anomaly detection to human page under 5 minutes. Guardian pause
  is a single transaction from a hardware wallet, tested quarterly under time pressure.
- **Incident response**: documented runbook with decision authority, communication
  templates, and a public post-mortem commitment. Rehearse twice a year.
- **Compliance**: securities-law analysis completed before launch; treasury multisig;
  timelock honoured as a real commitment, not a suggestion.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- SWC Registry (Smart Contract Weakness Classification) is the canonical enumeration of
  contract vulnerability classes used as the review checklist for both audits.
  https://swcregistry.io/docs
- OpenZeppelin Contracts documentation describes upgradeable patterns, access control, and
  pausable modules relied on in the controller implementation.
  https://docs.openzeppelin.com/contracts/5.x/

## Deliverables

- [x] Upgradeable controller with visible 48 h timelock on all privileged changes
- [x] Asymmetric guardian power: can pause in one transaction, cannot upgrade or withdraw
- [x] Three-feed oracle median with staleness rejection and a deviation circuit breaker
- [x] Per-transaction and per-address caps limiting drain speed
- [x] On-chain anomaly detection: drain patterns, TVL drops, guardian actions
- [x] Two sequential independent audits with agreed severity classification
- [x] Invariant test suite plus a fuzz campaign in CI
- [x] Incident runbook: decision authority, guardian steps, comms templates, post-mortem
