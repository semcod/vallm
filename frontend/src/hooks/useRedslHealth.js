import { useState, useEffect } from "react";
import { redslHealth, redslRefactor, getRedslStatus } from "../api";

export function useRedslHealth(projectPath) {
  const [health, setHealth] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refactorLoading, setRefactorLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getRedslStatus()
      .then(s => setStatus(s))
      .catch(() => setStatus({ available: false }));
  }, []);

  useEffect(() => {
    if (!projectPath || !status?.available) return;
    setLoading(true);
    redslHealth(projectPath)
      .then(h => { setHealth(h); setError(null); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectPath, status?.available]);

  async function handleRefactor() {
    setRefactorLoading(true);
    try {
      const result = await redslRefactor(projectPath, 5, true);
      if (result.status === "preview" && window.confirm("Apply these refactorings?")) {
        await redslRefactor(projectPath, 5, false);
        const h = await redslHealth(projectPath);
        setHealth(h);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setRefactorLoading(false);
    }
  }

  return { health, status, loading, refactorLoading, error, handleRefactor };
}
