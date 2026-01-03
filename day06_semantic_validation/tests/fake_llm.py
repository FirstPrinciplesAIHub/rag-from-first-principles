class FakeLLM:
    def __call__(self, prompt: str) -> str:
        lines = [line.rstrip() for line in prompt.splitlines()]

        claim = None
        for i, line in enumerate(lines):
            if line == "CLAIM:" and i + 1 < len(lines):
                claim = lines[i + 1].strip()
                break

        # Fail closed if claim is missing
        if claim is None:
            return (
                "LABEL: NOT_ENTAILED\n"
                "RATIONALE: Claim not found in prompt.\n"
                "SUPPORTING_CHUNKS: NONE"
            )

        if claim == "Refunds are processed within 5–7 business days.":
            return (
                "LABEL: ENTAILED\n"
                "RATIONALE: Explicitly stated in the policy.\n"
                "SUPPORTING_CHUNKS: c1"
            )

        if claim == "Refunds are instant.":
            return (
                "LABEL: NOT_ENTAILED\n"
                "RATIONALE: The context does not support instant refunds.\n"
                "SUPPORTING_CHUNKS: NONE"
            )

        return (
            "LABEL: UNKNOWN\n"
            "RATIONALE: Insufficient context.\n"
            "SUPPORTING_CHUNKS: NONE"
        )