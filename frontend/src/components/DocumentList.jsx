export default function DocumentList({ documents }) {
  return (
    <div className="panel">
      <h2>Documents</h2>
      {documents.length === 0 ? (
        <p className="muted">No documents uploaded yet.</p>
      ) : (
        <ul className="document-list">
          {documents.map((name) => (
            <li key={name}>{name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
