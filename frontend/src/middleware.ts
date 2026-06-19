import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Add paths that require authentication here
const protectedPaths = [
  '/trade-planner',
  '/journal',
  '/analytics',
  '/strategy-insights',
  '/ai-coach',
  '/settings'
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check if the path is protected
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path));
  
  // We check local storage state on the client side, but we can't reliably read local storage from middleware
  // For MVP, we will rely on client-side routing protection or Next.js layout protection.
  // Actually, we can check cookies if we use them, but we are using Zustand + LocalStorage.
  // We'll pass through here and let a client component handle redirects for MVP to avoid complexity with cookies.
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
