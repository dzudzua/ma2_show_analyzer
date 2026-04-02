-- grandMA2 preset export diagnostic helper
-- Paste this code into a plugin in the grandMA2 Plugin Pool and run it.
-- The goal is to compare how MA2 exports preset numbers in different scenarios:
-- 1. whole pool export
-- 2. contiguous range export
-- 3. single preset exports

return function()
    local function msg(text)
        if gma and gma.feedback then
            gma.feedback(text)
        end
    end

    local function cmd(text)
        msg('CMD: ' .. text)
        gma.cmd(text)
    end

    local function trim(text)
        if text == nil then
            return nil
        end
        return string.gsub(text, '^%s*(.-)%s*$', '%1')
    end

    local function split_csv(text)
        local result = {}
        local source = trim(text) or ''
        for token in string.gmatch(source, '([^,; ]+)') do
            local cleaned = trim(token)
            if cleaned ~= nil and cleaned ~= '' then
                table.insert(result, cleaned)
            end
        end
        return result
    end

    local prefix = 'presetdiag'
    local pool = '0'
    local rangeStart = '1'
    local rangeEnd = '20'
    local singles = '1,3,20,66'

    local answer = gma.textinput('Diagnostic file prefix', prefix)
    if answer ~= nil and answer ~= '' then
        prefix = trim(answer)
    end

    answer = gma.textinput('Preset pool to test', pool)
    if answer ~= nil and trim(answer) ~= '' then
        pool = trim(answer)
    end

    answer = gma.textinput('Range start inside pool', rangeStart)
    if answer ~= nil and trim(answer) ~= '' then
        rangeStart = trim(answer)
    end

    answer = gma.textinput('Range end inside pool', rangeEnd)
    if answer ~= nil and trim(answer) ~= '' then
        rangeEnd = trim(answer)
    end

    answer = gma.textinput('Single preset numbers (comma separated)', singles)
    if answer ~= nil and trim(answer) ~= '' then
        singles = trim(answer)
    end

    msg('Starting preset diagnostic export...')
    msg('Use these files to compare whether MA2 preserves real preset numbering.')
    msg('Files are exported to the currently selected drive/importexport folder.')

    cmd(string.format('Export Preset %s.1 Thru %s.999 "%s_pool_%s_full" /nc /o', pool, pool, prefix, pool))
    cmd(string.format('Export Preset %s.%s Thru %s.%s "%s_pool_%s_range_%s_%s" /nc /o', pool, rangeStart, pool, rangeEnd, prefix, pool, rangeStart, rangeEnd))

    local single_numbers = split_csv(singles)
    for _, number in ipairs(single_numbers) do
        local safe_number = string.gsub(number, '[^%w]+', '_')
        cmd(string.format('Export Preset %s.%s "%s_pool_%s_single_%s" /nc /o', pool, number, prefix, pool, safe_number))
    end

    msg('Preset diagnostic export finished.')
    msg('Compare XML contents for:')
    msg(string.format('- %s_pool_%s_full.xml', prefix, pool))
    msg(string.format('- %s_pool_%s_range_%s_%s.xml', prefix, pool, rangeStart, rangeEnd))
    msg('- individual single preset files')
    msg('Goal: find which export mode keeps the same preset numbering as in grandMA2.')
end
