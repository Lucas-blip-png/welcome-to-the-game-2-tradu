// Ferramenta para extrair/injetar literais de string do Assembly-CSharp.dll
// usando Mono.Cecil. Caminho AUTOMÁTICO recomendado para editar a DLL.
//
//   dotnet run -- extract <Assembly-CSharp.dll> <dll.json>
//   dotnet run -- inject  <Assembly-CSharp.dll> <dll.json> [saida.dll]
//
// "extract": gera/atualiza o catálogo (mantém as traduções já preenchidas).
// "inject":  reescreve cada literal cuja 'traducao' está preenchida e salva uma
//            nova DLL (por padrão Assembly-CSharp.translated.dll).
//
// O 'id' das entradas é "dll:" + sha1(fonte)[:12], idêntico ao tools/extract_dll.py,
// para que os dois extratores possam compartilhar o mesmo dll.json.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace WttgDllTool
{
    public class Entry
    {
        [JsonPropertyName("id")] public string Id { get; set; } = "";
        [JsonPropertyName("fonte")] public string Fonte { get; set; } = "";
        [JsonPropertyName("traducao")] public string Traducao { get; set; } = "";
        [JsonPropertyName("contexto")] public string? Contexto { get; set; }
    }

    public class Catalog
    {
        [JsonPropertyName("language")] public string Language { get; set; } = "pt-BR";
        [JsonPropertyName("game")] public string Game { get; set; } = "Welcome to the Game 2";
        [JsonPropertyName("source")] public string? Source { get; set; }
        [JsonPropertyName("note")] public string? Note { get; set; }
        [JsonPropertyName("entries")] public List<Entry> Entries { get; set; } = new List<Entry>();
    }

    public static class Program
    {
        static readonly JsonSerializerOptions JsonOpts = new JsonSerializerOptions
        {
            WriteIndented = true,
            Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        };

        static string DllId(string s)
        {
            using var sha1 = SHA1.Create();
            byte[] h = sha1.ComputeHash(Encoding.UTF8.GetBytes(s));
            return "dll:" + Convert.ToHexString(h).ToLowerInvariant().Substring(0, 12);
        }

        public static int Main(string[] args)
        {
            if (args.Length < 3)
            {
                Console.Error.WriteLine(
                    "Uso:\n" +
                    "  dotnet run -- extract <Assembly-CSharp.dll> <dll.json>\n" +
                    "  dotnet run -- inject  <Assembly-CSharp.dll> <dll.json> [saida.dll]");
                return 1;
            }

            switch (args[0])
            {
                case "extract":
                    return Extract(args[1], args[2]);
                case "inject":
                    return Inject(args[1], args[2], args.Length > 3 ? args[3] : "Assembly-CSharp.translated.dll");
                default:
                    Console.Error.WriteLine("ERRO: comando desconhecido: " + args[0]);
                    return 1;
            }
        }

        static Catalog LoadCatalog(string path)
        {
            if (File.Exists(path))
                return JsonSerializer.Deserialize<Catalog>(File.ReadAllText(path)) ?? new Catalog();
            return new Catalog { Source = "Assembly-CSharp.dll — literais (ldstr)" };
        }

        static int Extract(string dllPath, string catalogPath)
        {
            if (!File.Exists(dllPath)) { Console.Error.WriteLine("ERRO: não encontrei " + dllPath); return 1; }

            var module = ModuleDefinition.ReadModule(dllPath);
            var found = new Dictionary<string, Entry>();
            foreach (var type in module.GetTypes())
                foreach (var method in type.Methods)
                {
                    if (!method.HasBody) continue;
                    foreach (var ins in method.Body.Instructions)
                        if (ins.OpCode == OpCodes.Ldstr && ins.Operand is string s
                            && s.Trim().Length >= 2 && !found.ContainsKey(s))
                            found[s] = new Entry
                            {
                                Id = DllId(s),
                                Fonte = s,
                                Traducao = "",
                                Contexto = type.FullName + "::" + method.Name,
                            };
                }

            var cat = LoadCatalog(catalogPath);
            var byId = cat.Entries.ToDictionary(e => e.Id, e => e);
            int novos = 0;
            foreach (var e in found.Values)
                if (!byId.ContainsKey(e.Id)) { cat.Entries.Add(e); byId[e.Id] = e; novos++; }

            var dir = Path.GetDirectoryName(Path.GetFullPath(catalogPath));
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            File.WriteAllText(catalogPath, JsonSerializer.Serialize(cat, JsonOpts) + "\n");
            Console.WriteLine($"OK: {found.Count} literais únicos (+{novos} novos) -> {catalogPath}");
            return 0;
        }

        static int Inject(string dllPath, string catalogPath, string outPath)
        {
            if (!File.Exists(dllPath)) { Console.Error.WriteLine("ERRO: não encontrei " + dllPath); return 1; }
            if (!File.Exists(catalogPath)) { Console.Error.WriteLine("ERRO: não encontrei " + catalogPath); return 1; }

            var cat = LoadCatalog(catalogPath);
            var map = cat.Entries
                .Where(e => !string.IsNullOrEmpty(e.Traducao))
                .GroupBy(e => e.Fonte)
                .ToDictionary(g => g.Key, g => g.First().Traducao);
            if (map.Count == 0) { Console.WriteLine("Nada para injetar (sem traduções preenchidas)."); return 0; }

            var module = ModuleDefinition.ReadModule(dllPath);
            int n = 0;
            foreach (var type in module.GetTypes())
                foreach (var method in type.Methods)
                {
                    if (!method.HasBody) continue;
                    foreach (var ins in method.Body.Instructions)
                        if (ins.OpCode == OpCodes.Ldstr && ins.Operand is string s
                            && map.TryGetValue(s, out var tr))
                        { ins.Operand = tr; n++; }
                }

            var dir = Path.GetDirectoryName(Path.GetFullPath(outPath));
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            module.Write(outPath);
            Console.WriteLine($"OK: {n} literais traduzidos -> {outPath}");
            Console.WriteLine("Substitua o Assembly-CSharp.dll do jogo por este (faça backup antes).");
            return 0;
        }
    }
}
