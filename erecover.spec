// erecover replay attack

/*
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Rule: permit signature replay protection                                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
*/
rule permit_replay_protection(env e) {
    require nonpayable(e);

    address owner;
    address spender;
    uint256 amount;
    uint256 deadline;
    uint8 v;
    bytes32 r;
    bytes32 s;

    // Initial nonce
    uint256 initialNonce = nonces(owner);

    // Call permit function
    permit@withrevert(e, owner, spender, amount, deadline, v, r, s);
    bool success = !lastReverted;

    // Ensure nonce is incremented
    assert success => nonces(owner) == initialNonce + 1;

    // Attempt to reuse the same signature
    permit@withrevert(e, owner, spender, amount, deadline, v, r, s);
    bool replaySuccess = !lastReverted;

    // Ensure the second call fails
    assert !replaySuccess;
}