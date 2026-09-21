type HealthResponse = {
  status?: string;
};

async function getBackendStatus(): Promise<"connected" | "disconnected"> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  try {
    const response = await fetch(`${apiBaseUrl}/health`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!response.ok) {
      return "disconnected";
    }

    const data = (await response.json()) as HealthResponse;
    return data.status === "ok" ? "connected" : "disconnected";
  } catch {
    return "disconnected";
  }
}

export default async function Home() {
  const backendStatus = await getBackendStatus();
  const isConnected = backendStatus === "connected";

  return (
    <main>
      <p className="eyebrow">Music Recommendation</p>
      <h1>Build the listening loop before the model.</h1>
      <p className="summary">
        A minimal foundation for the product: Next.js on the frontend, FastAPI on the backend,
        and room for Supabase migrations and recommender experiments.
      </p>
      <section className="status-panel" aria-label="Backend health status">
        <div className="status-copy">
          <span className="status-label">Backend</span>
          <span className="status-value">
            {isConnected ? "connected" : "disconnected"}
          </span>
        </div>
        <span
          className={`status-indicator ${isConnected ? "connected" : "disconnected"}`}
          aria-hidden="true"
        />
      </section>
    </main>
  );
}
