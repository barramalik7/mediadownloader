import { createRootRoute, Link, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import { Download } from 'lucide-react'
import { ThemeProvider } from '@/components/theme-provider'
import { ModeToggle } from '@/components/mode-toggle'

export const Route = createRootRoute({
    component: () => (
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <div className="min-h-screen flex flex-col bg-background text-foreground font-sans antialiased">
                <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                    <div className="container flex h-14 max-w-screen-2xl items-center justify-between">
                        <div className="mr-4 flex gap-2 font-bold items-center">
                            <div className="p-1 rounded-lg bg-primary text-primary-foreground">
                                <Download className="h-5 w-5" />
                            </div>
                            <Link to="/" className="flex items-center space-x-2">
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
            <TanStackRouterDevtools />
        </ThemeProvider>
    ),
})
