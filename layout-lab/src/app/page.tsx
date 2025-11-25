
import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-100 flex flex-col">
      
      <header className="invisible w-full px-6 py-4 flex justify-between items-center border-b border-gray-300 bg-white">
        <h1 className='text-2xl font-bold tracking-tight'>Layout Lab</h1>
        <nav>
          <Link href ="/spacelayout" className='hover:text-black'>Layout Experiment</Link>
        </nav>
      </header>
      
      {/* Hero Section */}
     
      <section className='flex flex-col items-center text-center pt-20'>
        <h2 className='text-4xl font-extrabold mb-4 leading-tight'> Room Layout Algorithm Lab </h2>
        <p className='text-gray-600 text-lg max-w-2xl mb-8'> Explore various room layout algorithms and their implementations such as BFS/CSP </p>
        <Link href="/spacelayout" className='bg-black text-white px-8 py-4 rounded-lg text-lg font-medium  hover:bg-gray-800 transition'> Go to Layout Lab </Link>
      
      </section>
      {/* Feature Highlights */}
      <section className='grid grid-cols-1 sm:grid-cols-3 gap-8 px-8 py-20 max-w-6xl mx-auto'>
        <h2 className='hidden'> Features </h2>
        <div className='bg-white p-6 rounded-xl shadow-sm border'>
          <h3 className='font-semibold text-xl mb-2 text-center'>Multiply Layout Policies</h3>
          <p className='text-gray-600'> Experiment with different layout policies to see how they affect room arrangements. </p>
        </div>

        <div className='bg-white p-6 rounded-xl shadow-xl border'>
          <h3 className='font-semibold text-xl mb-2 text-center'>Algorithm Visualization</h3>
          <p className='text-gray-600'> Visualize how different algorithms approach the layout problem step-by-step. </p>
        </div>

        <div className='bg-white p-6 rounded-xl shadow-xl border'>
          <h3 className='font-semibold text-xl mb-2 text-center'> Pixelize geometry engine</h3>
          <p className='text-gray-600'> Utilize a pixel-based geometry engine for precise layout calculations and rendering. </p>
        </div>
      </section>

      <footer className='mt-auto py-6 text-center text-gray-200 border-t'> 
        <p> © 2025 ACE AI. All rights reserved. </p>
      </footer>
      
    </main>
  );
}