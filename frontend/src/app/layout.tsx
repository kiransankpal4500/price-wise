import type { Metadata } from 'next';
import { Outfit } from 'next/font/google';
import './globals.css';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';

const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit' });

export const metadata: Metadata = {
  title: 'PriceWise — Approachable Intelligence in Shopping',
  description:
    'Instant price comparison across Amazon, Flipkart, Blinkit, Zepto, Swiggy Instamart, Myntra & Nykaa. Find the lowest price and best deal in seconds.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${outfit.className} bg-[#f8f9ff] text-slate-900 antialiased min-h-screen flex flex-col justify-between selection:bg-violet-500 selection:text-white`}>
        <div className="flex flex-col min-h-screen">
          <Header />
          <main className="flex-grow">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
