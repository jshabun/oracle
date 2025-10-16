import { useState } from 'react'

export default function DraftMode() {
  const [draftPosition, setDraftPosition] = useState(1)
  const [draftStarted, setDraftStarted] = useState(false)
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-800">Draft Mode</h2>
        {!draftStarted && (
          <button
            onClick={() => setDraftStarted(true)}
            className="px-6 py-3 bg-oracle-orange text-white rounded-lg font-semibold hover:bg-opacity-90 transition"
          >
            Start Draft Session
          </button>
        )}
      </div>
      
      {!draftStarted ? (
        <div className="bg-white p-8 rounded-lg shadow-md max-w-2xl mx-auto">
          <h3 className="text-2xl font-semibold text-gray-800 mb-6">Draft Setup</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Draft Position
              </label>
              <select
                value={draftPosition}
                onChange={(e) => setDraftPosition(Number(e.target.value))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oracle-orange focus:border-transparent"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(pos => (
                  <option key={pos} value={pos}>Position {pos}</option>
                ))}
              </select>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">Draft Strategy Tips:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Consider punt strategies based on your draft position</li>
                <li>• Balance counting stats with percentages</li>
                <li>• Don't reach for TO-heavy playmakers early</li>
                <li>• Elite centers (Jokic, Embiid, AD) provide positional scarcity</li>
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Draft Recommendations */}
          <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              Recommended Picks
            </h3>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-oracle-orange text-white rounded-full flex items-center justify-center font-bold">
                      {i}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">Player Name</div>
                      <div className="text-sm text-gray-500">PG/SG - Team</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-oracle-blue">Value: 8.5</div>
                    <div className="text-xs text-gray-500">Rank: {i * 3}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Your Draft */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Your Picks</h3>
            <div className="text-gray-500 text-center py-8">
              No picks yet
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
