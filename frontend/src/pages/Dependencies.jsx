import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, AlertCircle, Download } from 'lucide-react'
import { checkDependencies, installDependency } from '../api'

export default function Dependencies() {
  const queryClient = useQueryClient()
  
  const { data: dependencies, isLoading } = useQuery({
    queryKey: ['dependencies'],
    queryFn: checkDependencies
  })
  
  const installMutation = useMutation({
    mutationFn: installDependency,
    onSuccess: () => {
      queryClient.invalidateQueries(['dependencies'])
    }
  })
  
  if (isLoading) {
    return <div>Loading...</div>
  }
  
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">System Dependencies</h2>
        <p className="text-gray-600 mt-1">Manage required and optional system components</p>
      </div>
      
      <div className="grid gap-4">
        {Object.entries(dependencies || {}).map(([key, dep]) => (
          <DependencyCard
            key={key}
            depKey={key}
            {...dep}
            onInstall={() => installMutation.mutate(key)}
            isInstalling={installMutation.isPending}
          />
        ))}
      </div>
    </div>
  )
}

function DependencyCard({ depKey, name, description, installed, required, version, onInstall, isInstalling }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            {installed ? (
              <CheckCircle className="text-green-600" size={24} />
            ) : (
              <AlertCircle className={required ? 'text-red-600' : 'text-gray-400'} size={24} />
            )}
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{name}</h3>
              <p className="text-sm text-gray-600">{description}</p>
            </div>
          </div>
          
          <div className="mt-3 flex items-center gap-4 text-sm">
            <span className={`font-medium ${installed ? 'text-green-600' : required ? 'text-red-600' : 'text-gray-500'}`}>
              {installed ? 'Installed' : 'Not installed'}
            </span>
            {required && (
              <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">
                Required
              </span>
            )}
            {version && (
              <span className="text-gray-500">{version}</span>
            )}
          </div>
        </div>
        
        {!installed && (
          <button
            onClick={onInstall}
            disabled={isInstalling}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download size={16} />
            {isInstalling ? 'Installing...' : 'Install'}
          </button>
        )}
      </div>
    </div>
  )
}
