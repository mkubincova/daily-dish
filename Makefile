.PHONY: verify

# Mirrors `npm run verify`. Both invoke scripts/verify.sh; pick whichever feels natural.
verify:
	@bash scripts/verify.sh
