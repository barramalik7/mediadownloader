/// <reference types="vite/client" />
import {
    HeadContent,
    Link,
    Outlet,
    Scripts,
    createRootRouteWithContext,
} from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { QueryClientProvider } from '@tanstack/react-query'
import * as React from 'react'
import type { QueryClient } from '@tanstack/react-query'
import { Download } from 'lucide-react'
import { ThemeProvider } from '@/components/theme-provider'
import { ModeToggle } from '@/components/mode-toggle'
import appCss from '@/index.css?url'

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()(
    {
        head: () => ({
            meta: [
                { charSet: 'utf-8' },
                {
                    name: 'viewport',
                    content: 'width=device-width, initial-scale=1',
                },
                {
                    title: 'Media Downloader',
                },
                {
                    name: 'description',
                    content:
                        'Download videos and media from YouTube, TikTok, Instagram, Twitter, Pinterest, and Spotify.',
                },
            ],
            links: [
                { rel: 'stylesheet', href: appCss },
                { rel: 'icon', type: 'image/svg+xml', href: '/vite.svg' },
            ],
        }),
        notFoundComponent: () => (
            <div className="flex items-center justify-center min-h-[50vh]">
                <div className="text-center">
                    <h1 className="text-4xl font-bold mb-2">404</h1>
                    <p className="text-muted-foreground">Page not found</p>
                </div>
            </div>
        ),
        component: RootComponent,
    },
)

function RootComponent() {
    const { queryClient } = Route.useRouteContext()

    return (
        <RootDocument>
            <QueryClientProvider client={queryClient}>
                <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
                    <div className="min-h-screen flex flex-col bg-background text-foreground font-sans antialiased">
                        <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                            <div className="container flex h-14 max-w-screen-2xl items-center justify-between">
                                <div className="mr-4 flex gap-2 font-bold items-center">
                                    <div className="p-1 rounded-lg bg-primary text-primary-foreground">
                                        <Download className="h-5 w-5" />
                                    </div>
                                    <Link
                                        to="/"
                                        className="flex items-center space-x-2"
                                    >
                                        <span>Media Downloader</span>
                                    </Link>
                                </div>
                                <div className="flex items-center gap-2">
                                    <ModeToggle />
                                </div>
                            </div>
                        </header>
                        <main className="flex-1">
                            <Outlet />
                        </main>
                    </div>
                </ThemeProvider>
                <ReactQueryDevtools buttonPosition="bottom-left" />
            </QueryClientProvider>
        </RootDocument>
    )
}

function RootDocument({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en" suppressHydrationWarning>
            <head>
                <HeadContent />
            </head>
            <body>
                {children}
                <TanStackRouterDevtools position="bottom-right" />
                <Scripts />
            </body>
        </html>
    )
}
