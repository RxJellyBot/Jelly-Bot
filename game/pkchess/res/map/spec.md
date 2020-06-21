### Map File Specification

The following specification is listed as its expected order. 

**Failed to completely follow the specification 
will either crash the application or have an incorrect parse result.**

The implementation of the map file loading method will heavily rely on this specification. 
        
- A line containing defining the dimension of the map

    - Separate by a single space
    
    - The 1st element is WIDTH, the 2nd element is HEIGHT
    
    - Example:
      ```
      9 10
      ```

- A rectangle representing the initial status of the map

    - The content is a single digit number, representing the initial `MapPointStatus` in `int`
    
    - Must match the dimension defined above
    
    - Example:
      ```
      111
      111
      121
      ```
    
- Lines representing the resource spawning points

    - A line separated by a single space, where the 1st element represents `MapPointResource` in `int`
      and the rest of the elements represents the spawning point in the format of `X,Y`
      
    - Both `X` and `Y` for coords starts from 0 
    
    - `0,0` at the top left corner
     
    - Down to increase `X`; Right to increase `Y`
      
    - Resource type which will not be spawned in the map does not need to be listed
    
    - Example (Skipping resource type 2):
      ```
      1 1,1 3,3 5,6
      3 1,2 1,3 2,5
      ```

Example file

    4 4
    1111
    1121
    1211
    1111
    1 0,0 2,2
    2 1,1 3,3