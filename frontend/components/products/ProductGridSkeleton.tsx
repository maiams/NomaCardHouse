import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

interface ProductGridSkeletonProps {
  count?: number;
}

export function ProductGridSkeleton({ count = 10 }: ProductGridSkeletonProps) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i} className="overflow-hidden">
          <Skeleton className="aspect-[3/4] w-full" />
          <CardContent className="p-4">
            <Skeleton className="h-5 w-full" />
            <Skeleton className="mt-2 h-4 w-2/3" />
          </CardContent>
          <CardFooter className="p-4 pt-0">
            <Skeleton className="h-6 w-24" />
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
