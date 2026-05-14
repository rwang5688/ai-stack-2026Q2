// Baseline permit for all tools on the student services gateway
permit (
  principal,
  action,
  resource is AgentCore::Gateway
);
