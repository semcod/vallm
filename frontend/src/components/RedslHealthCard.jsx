import { useRedslHealth } from "../hooks/useRedslHealth";
import { StatusChecking, StatusUnavailable, StatusLoading, StatusError, HealthContent } from "./RedslHealthCard.parts";

export function RedslHealthCard({ projectPath, repo }) {
  const { health, status, loading, refactorLoading, error, handleRefactor } = useRedslHealth(projectPath);

  if (!status) return <StatusChecking />;
  if (!status.available) return <StatusUnavailable />;
  if (loading) return <StatusLoading />;
  if (error && !health) return <StatusError error={error} />;

  return <HealthContent health={health} refactorLoading={refactorLoading} onRefactor={handleRefactor} repo={repo} />;
}
