import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const TestModule = buildModule("TestModule", (m) => {
  const test = m.contract("Test", []);

  return { test };
});

export default TestModule;
