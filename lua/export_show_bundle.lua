-- grandMA2 cue-list export helper
-- Paste this code into a plugin in the grandMA2 Plugin Pool and run it.
-- It asks for the main Sequence (main cue list) and then exports the full show context,
-- including patch as transformed CSV for direct analyzer input.

return function()
    local function msg(text)
        if gma and gma.feedback then gma.feedback(text) end
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

    local prefix = 'showbundle'

    local answer = gma.textinput('Export file prefix', prefix)
    if answer ~= nil and answer ~= '' then
        prefix = answer
    end

    local sequenceRange = gma.textinput('Main Sequence or range', '1')
    if sequenceRange == nil or trim(sequenceRange) == '' then
        sequenceRange = '1'
    end
    sequenceRange = trim(sequenceRange)

    local maxPool = gma.textinput('Max object number per pool', '999')
    if maxPool == nil or maxPool == '' then
        maxPool = '999'
    end
    maxPool = trim(maxPool)

    local driveNo = gma.textinput('Target drive: 1=internal, 4=USB', '4')
    if driveNo == nil or driveNo == '' then
        driveNo = '4'
    end
    driveNo = trim(driveNo)

    msg('Starting cue-list export...')
    msg('Selecting target drive ' .. driveNo .. ' ...')
    cmd('SelectDrive ' .. driveNo)
    msg('Files are exported to the selected drive/importexport folder.')
    msg('Main cue list for analysis: Sequence ' .. sequenceRange)
    msg('Patch will be exported in the same run as transformed CSV.')

    cmd('Export Sequence ' .. sequenceRange .. ' "' .. prefix .. '_main_sequences" /nc /o')
    cmd('Export Sequence 1 Thru ' .. maxPool .. ' "' .. prefix .. '_all_sequences" /nc /o')
    cmd('Export Group 1 Thru ' .. maxPool .. ' "' .. prefix .. '_groups" /nc /o')
    cmd('Export Effect 1 Thru ' .. maxPool .. ' "' .. prefix .. '_effects" /nc /o')
    cmd('Export Fixture 1 Thru ' .. maxPool .. ' "' .. prefix .. '_patch" /style=csv /transform /o')
    for p = 0, 14 do
        local filename = string.format('%s_preset_%d', prefix, p)
        local command = string.format('Export Preset %d.1 Thru %d.%s "%s" /nc /o', p, p, maxPool, filename)
        cmd(command)
    end

    msg('Cue-list export finished.')
    msg('Expected patch file for analyzer: ' .. prefix .. '_patch.csv')
    if driveNo == '1' then
        msg('Target: internal drive')
    elseif driveNo == '4' then
        msg('Target: USB flash drive')
    else
        msg('Target drive number: ' .. driveNo)
    end
    msg('Copy exported files into the analyzer exports folder and run run_analysis.bat.')
end
