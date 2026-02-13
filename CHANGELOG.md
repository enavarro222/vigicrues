# Changelog

## NEXT RELEASE

- Convert coordinates to WGS84 using `pyproj`.
- Add `pyproj` as a dependency.
- Add error handling when no observations found in CLI.
- Add search method override with details loading (and filtering of non existing stations).
- Catch http error for better message on cli "get" method.
- Add a filtering of closed stations in search results.

## [0.1.0] - 2026-02-12

- Initial release with basic functionality to search for stations and retrieve observations.
