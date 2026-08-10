import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChatMessage from "./ChatMessage.jsx";

describe("ChatMessage", () => {
  it("renders the answer text and its sources", () => {
    render(
      <ChatMessage
        role="ai"
        text="This document discusses LocalDoc AI."
        sources={[{ document: "sample.pdf", page: 2 }]}
      />
    );

    expect(screen.getByText(/This document discusses LocalDoc AI\./)).toBeInTheDocument();
    expect(screen.getByText(/sample.pdf - page 2/)).toBeInTheDocument();
  });

  it("renders a user message without a source list", () => {
    render(<ChatMessage role="user" text="What is this document about?" sources={[]} />);

    expect(screen.getByText(/What is this document about\?/)).toBeInTheDocument();
    expect(screen.queryByText(/Sources:/)).not.toBeInTheDocument();
  });
});
