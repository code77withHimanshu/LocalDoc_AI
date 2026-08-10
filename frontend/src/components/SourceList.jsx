export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="source-list">
      <strong>Sources:</strong>
      <ul>
        {sources.map((source, index) => (
          <li key={index}>
            {source.document}
            {source.page != null ? ` - page ${source.page}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}
