export default function TeamManagement() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">My Team</h2>
      
      {/* Current Roster */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Current Roster</h3>
        <div className="text-gray-500 text-center py-8">
          Connect to Yahoo Fantasy to view your roster
        </div>
      </div>
      
      {/* Team Stats */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Team Category Performance</h3>
        <div className="grid grid-cols-3 md:grid-cols-9 gap-4">
          {['FG%', 'FT%', '3PM', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO'].map(cat => (
            <div key={cat} className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-sm font-semibold text-gray-600">{cat}</div>
              <div className="text-2xl font-bold text-gray-800 mt-1">-</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
