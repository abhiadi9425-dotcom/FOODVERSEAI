import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App";

// Mock fetch for health and initial API calls
global.fetch = vi.fn().mockImplementation((url) => {
  if (url.includes("/health")) {
    return Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({
          status: "healthy",
          database_connected: true,
          ai_providers: {
            active_provider: "fallback",
            gemini_configured: false,
            openai_configured: false,
            usda_live_configured: false,
            verified_reference_db: "Active (USDA FoodData Central)",
          },
          version: "1.0.0",
        }),
    });
  }
  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve([]),
  });
});

describe("FoodVerse AI App", () => {
  it("renders FoodVerse AI headline and branding on landing page", () => {
    render(<App />);
    const branding = screen.getAllByText(/FoodVerse/i);
    expect(branding.length).toBeGreaterThan(0);
    expect(
      screen.getByText(/Intelligent Nutrition, Culinary & Kitchen Analysis/i)
    ).toBeInTheDocument();
  });

  it("renders Start Analyzing Food call to action", () => {
    render(<App />);
    const ctaButtons = screen.getAllByText(/Start Analyzing Food/i);
    expect(ctaButtons.length).toBeGreaterThan(0);
  });
});
