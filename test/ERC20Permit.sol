
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

import "forge-std/Test.sol";
import "../ERC20Permit.sol";
import "../ERC20.sol";

contract ERC20PermitTest is Test {
    ERC20Permit token;
    address owner;
    address spender;

    function setUp() public {
        owner = address(0x123);
        spender = address(0x456);
        token = new ERC20PermitMock("TestToken", "TTK");
        token.mint(owner, 1000 * 10 ** 18);
    }

    function testPermit() public {
        uint256 amount = 100 * 10 ** 18;
        uint256 nonce = token.nonces(owner);
        uint256 deadline = block.timestamp + 1 days;

        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                owner,
                spender,
                amount,
                nonce,
                deadline
            )
        );

        bytes32 domainSeparator = token.domainSeparators(block.chainid);
        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                domainSeparator,
                structHash
            )
        );

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(uint256(owner), digest);

        vm.prank(owner);
        token.permit(owner, spender, amount, deadline, v, r, s);

        assertEq(token.allowance(owner, spender), amount);
        assertEq(token.nonces(owner), nonce + 1);
    }

    function testPermitExpired() public {
        uint256 amount = 100 * 10 ** 18;
        uint256 nonce = token.nonces(owner);
        uint256 deadline = block.timestamp - 1 days;

        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                owner,
                spender,
                amount,
                nonce,
                deadline
            )
        );

        bytes32 domainSeparator = token.domainSeparators(block.chainid);
        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                domainSeparator,
                structHash
            )
        );

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(uint256(owner), digest);

        vm.prank(owner);
        vm.expectRevert("ERC20Permit: expired deadline");
        token.permit(owner, spender, amount, deadline, v, r, s);
    }

    function testPermitInvalidSignature() public {
        uint256 amount = 100 * 10 ** 18;
        uint256 nonce = token.nonces(owner);
        uint256 deadline = block.timestamp + 1 days;

        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                owner,
                spender,
                amount,
                nonce,
                deadline
            )
        );

        bytes32 domainSeparator = token.domainSeparators(block.chainid);
        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                domainSeparator,
                structHash
            )
        );

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(uint256(spender), digest);

        vm.prank(owner);
        vm.expectRevert("ERC20Permit: invalid signature");
        token.permit(owner, spender, amount, deadline, v, r, s);
    }
}

contract ERC20PermitMock is ERC20Permit {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}

    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    }
}