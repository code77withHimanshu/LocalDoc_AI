import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import DocumentUpload from "./DocumentUpload.jsx";

describe("DocumentUpload", () => {
  it("shows an error when uploading without choosing a file", () => {
    const onError = vi.fn();
    render(<DocumentUpload onUploaded={vi.fn()} onError={onError} />);

    fireEvent.click(screen.getByText("Upload"));

    expect(onError).toHaveBeenCalledWith("Please choose a file first");
  });
});
