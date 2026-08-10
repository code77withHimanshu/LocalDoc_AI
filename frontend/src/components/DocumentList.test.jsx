import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import DocumentList from "./DocumentList.jsx";

describe("DocumentList", () => {
  it("shows a message when there are no documents", () => {
    render(<DocumentList documents={[]} onDelete={vi.fn()} />);

    expect(screen.getByText(/No documents uploaded yet/)).toBeInTheDocument();
  });

  it("calls onDelete with the document name when Remove is clicked", async () => {
    const onDelete = vi.fn().mockResolvedValue();
    render(<DocumentList documents={["sample.pdf"]} onDelete={onDelete} />);

    fireEvent.click(screen.getByText("Remove"));

    await waitFor(() => expect(onDelete).toHaveBeenCalledWith("sample.pdf"));
  });
});
