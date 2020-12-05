import Environment as env
import copy

class util:
    @staticmethod
    def diagonal_mahattan_heuristic (A,B:list):  # A is [x,y]; B is [x,y]
        return max(abs(A[0]-B[1]), abs(A[1]-B[1]))
    """
    - start is [xs,ys]; goal is [xg,yg] (1 start 1 goal)
    - heuristicFunction is a function (list2, list2):
        Ex def heuristic(A,B):
                return max(abs(A[0]-B[0]), abs(A[1]-B[1]))
        then pass heuristicFunction to A,B
        Passing heuristicFunction none make heuristic value 0.
    - Distance between two neighbor is assumed 1
    - Return [distance, route]
        distance is integer, minimum distance from start to goal.
        route is [[xs,ys],[x1,y1],...,[xk,yk],[xg,yg]]
    - if goal is not reachable from start, then returned distance is -1 and route is []
    - Pass custom dx or dy if you want another-type of neighbor (the array -1, 0, 1 one)
    - Algorithm: A* without heap O(n^4 complexity) on worst case
    """
    @staticmethod
    def astar (environment, start, goal,heuristicFunction=None, dr=[-1,-1,0,1,1,1,0,-1], dc=[0,-1,-1,-1,0,1,1,1]):
        nr, nc=[environment.rows, environment.columns]

        def inside (r, c):    
            return r>=0 and r<nr and c>=0 and c<nc
        def iswall (r, c):
            return environment.board[r][c] == 1
        def heuristic (A, B):
            if heuristicFunction is not None:
                return heuristicFunction(A,B)
            else:
                return 0

        xg, yg = goal
        r,c = start
        xs, ys = start
        # Now A Star to goal      
        parent=[]; cost=[]
        frontier=[]

        for i in range(nr):
            tmp=[]; tmp2=[]
            for j in range(nc):
                tmp.append([]); tmp2.append(999999)
            parent.append(tmp); cost.append(tmp2)

        cost[r][c]=0; frontier.append([r,c])

        def foundGoal():
            return parent[xg][yg] != []

        # Cost is g
        while (frontier!=[] and not foundGoal()):
            Min=999999
            r,c=frontier[0];i=0
            for j in range(len(frontier)):
                f=frontier[j]
                if (cost[f[0]][f[1]]+heuristic(f,goal) < Min):
                    Min=cost[f[0]][f[1]]+heuristic(f,goal)
                    r,c=f
                    i=j
            frontier.pop(i)

            for k in range(len(dr)):
                rr=r+dr[k]; cc=c+dc[k]
                if inside(rr,cc) and not iswall(rr,cc) and cost[r][c]+1 < cost[rr][cc]:
                    cost[rr][cc]=cost[r][c]+1
                    parent[rr][cc]=[r,c]
                    frontier.append([rr,cc])
        
        if (parent[xg][yg] == []):  # No way to reach goal
            return [-1,[]]
        trace_x,trace_y = [xg, yg]
        dist=cost[xg][yg];route=[]
        save_x = -1; save_y = -1
        while trace_x != xs and trace_y != ys:
            save_x, save_y = parent[trace_x][trace_y]
            route.append([save_x, save_y])
            trace_x = save_x; trace_y = save_y
        return [dist, route]

    @staticmethod
    def getEvironmentIncludeObs (environment, obstacleArray):
        env=copy.deepcopy(environment)
        map=env.board
        if obstacleArray is None:
            return env
        for obs in obstacleArray:
            tr, tc=obs.upperLeft
            sr, sc=obs.size
            for i in range(sr):
                for j in range(sc):
                    map[tr+i][tc+j] = 1   # Obstacle --> Wall
        return env