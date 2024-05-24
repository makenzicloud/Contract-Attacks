/***
 * #  ERC20 Example
 *
 * We use this to search ERC20 bugs.
 */

methods {
    function totalSupply()                          external returns(uint) envfree;
    function balanceOf(address)                     external returns(uint) envfree;
    function allowance(address,address)             external returns(uint) envfree;
    function transfer(address,uint)                 external;
    function transferFrom(address,address,uint)     external;
    function approve(address,uint)                  external;
    function recoverERC20(address,uint256)          external;
}

//// ## Part 1: Basic rules ////////////////////////////////////////////////////

rule reachability(method f)
{
    env e;
    calldataarg args;
    f(e,args);
    satisfy true, "a non-reverting path through this method was found";
}

/// Transfer must move `amount` tokens from the caller's account to `recipient`
rule transferSpec {
    address sender; address recipient; uint amount;

    require sender != recipient;

    env e;
    require e.msg.sender == sender;

    mathint balance_sender_before = balanceOf(sender);
    mathint balance_recipient_before = balanceOf(recipient);

    transfer(e, recipient, amount);

    mathint balance_sender_after = balanceOf(sender);
    mathint balance_recipient_after = balanceOf(recipient);

    assert balance_sender_after == balance_sender_before - amount,
        "transfer must decrease sender's balance by amount";

    assert balance_recipient_after == balance_recipient_before + amount,
        "transfer must increase recipient's balance by amount";
}

/// Transfer must revert if the sender's balance is too small
rule transferReverts {
    env e; address recipient; uint amount;

    require balanceOf(e.msg.sender) < amount;

    transfer@withrevert(e, recipient, amount);

    assert lastReverted,
        "transfer(recipient, amount) must revert if sender's balance is less than `amount`";
}

//// ## Part 2: Parametric rules ///////////////////////////////////////////////

/// If `approve` changes a holder's allowance, then it was called by the holder
rule onlyHolderCanChangeAllowance {
    env e;
    method f;
    address holder;
    address spender;
    uint256 amount;

    mathint allowance_before = allowance(holder, spender);

    
    approve(e, spender, amount);

    mathint allowance_after = allowance(holder, spender);

    assert allowance_after > allowance_before => e.msg.sender == holder,
        "only the holder can increase their allowance";
}
/*
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Rule: check total amount after total supply after mint                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
*/
rule onlyHolderCanChangeSupply {
    env e;
    method f;
    address holder;
    address spender;
    uint256 amount;

    mathint TotalSupplyBefore = totalSupply();

    calldataarg args;
    f(e, args);
    
    mathint TotalSupply_after = totalSupply();

    assert  e.msg.sender == _owner() => TotalSupply_after != TotalSupplyBefore;

   
}



/*
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Rule: check total amount after total supply after mint                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
*/
// rule totalSupplyAfterMint(address account, uint256 amount) {
//     env e;
//     mint(e, account, amount);

//     uint256 userBalanceAfterMint = balanceOf(account);
//     uint256 totalSupplyAfterMint = totalSupply();

//     // check that the current balance is at least total supply amount
//     assert totalSupplyAfterMint >= userBalanceAfterMint, 
//     "total must be should be more than balance of user";
// }


//// ## Part 5: Initial State ////////////////////////////////////////////////////

/// Initial State: Total Supply is initialized to zero
// invariant initialState {
//     to_mathint(totalSupply()) == 0;
// }
