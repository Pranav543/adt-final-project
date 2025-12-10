import React from 'react';
import { 
  LayoutDashboard, 
  Layers, 
  FileCode, 
  Users, 
  ArrowLeftRight,
  TrendingUp 
} from 'lucide-react';

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', active: true },
  { icon: Layers, label: 'Protocols', active: false },
  { icon: FileCode, label: 'Contracts', active: false },
  { icon: Users, label: 'Users', active: false },
  { icon: ArrowLeftRight, label: 'Transactions', active: false },
  { icon: TrendingUp, label: 'Market', active: false },
];

const Sidebar = () => {
  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen p-4">
      <nav className="mt-8">
        <ul className="space-y-2">
          {menuItems.map((item, index) => (
            <li key={index}>
              <a
                href="#"
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                  item.active
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <item.icon className="h-5 w-5" />
                <span>{item.label}</span>
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
