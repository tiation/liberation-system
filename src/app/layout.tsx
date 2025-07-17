import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '../styles/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Liberation System - One Person, Massive Impact',
  description: 'A minimal system to flip everything on its head. Trust by default, resources for everyone, truth over marketing.',
  keywords: ['liberation', 'system', 'automation', 'trust', 'resources', 'truth', 'transformation'],
  authors: [{ name: 'Tiation', url: 'https://github.com/tiation-github' }],
  creator: 'Tiation',
  publisher: 'Tiation',
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    title: 'Liberation System',
    description: 'One person, massive impact. Transform everything.',
    url: 'https://github.com/tiation-github/liberation-system',
    siteName: 'Liberation System',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Liberation System',
    description: 'One person, massive impact. Transform everything.',
    images: ['/og-image.png'],
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: '#00ffff',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div id="__next">{children}</div>
      </body>
    </html>
  );
}
